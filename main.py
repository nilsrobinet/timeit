"""Main app for TimeIt. Contains the API."""

import os
import datetime
import json
from typing import Any

import cherrypy
from src.time_keeper import TimeKeeper
from src.attendance import Attendance
from src.time_util import get_week_start, duration_delta, parse_iso_datetime
from src.config_handler import ConfigHandler

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


class TimeIt(object):
    """TimeIt cherrypy web app."""

    def __init__(self):
        self.config = ConfigHandler(os.path.join(APP_ROOT, "config/userconf.toml"))
        self.config.load()
        self.time_keeper = TimeKeeper(os.path.join(APP_ROOT, self.config.get_timekeeping_path()))
        self.time_keeper.load_data()
        self.attendance = Attendance(os.path.join(APP_ROOT, self.config.get_attendance_path()))
        self.attendance.load_attendance()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def api(self, *vpath, **params) -> dict[str, Any] | None:
        """Handle API requests.
        :param vpath: API resource path components.
        :param params: Query parameters for the request.
        :returns: The API response payload.
        """
        self.time_keeper.reload_if_changed()
        self.attendance.reload_if_changed()
        method = cherrypy.request.method.upper()

        if not vpath:
            raise cherrypy.HTTPError(404, "Missing API resource")

        resource = vpath[0]
        handled = True
        response = None
        if resource == "entries":
            if method == "GET" and len(vpath) == 1:
                response = self._entries_get(params)
            elif method == "POST" and len(vpath) == 1:
                payload = self._read_json_body(required=True)
                response = self._entries_post(payload)
            elif method == "PATCH" and len(vpath) == 2:
                payload = self._read_json_body(required=True)
                response = self._entries_patch(vpath[1], payload)
            elif method == "DELETE" and len(vpath) == 2:
                self._entries_delete(vpath[1])
            else:
                handled = False
        elif resource == "summary" and method == "GET":
            response = self._summary_get(params)
        elif resource == "history" and method == "GET":
            response = self._history_get(params)
        elif resource == "config" and method == "GET":
            response = self.config.get_config()
        elif resource == "attendance" and method == "GET":
            response = self._attendance_get()
        elif resource == "attendance" and method == "POST":
            response = self._attendance_post(params)
        else:
            handled = False

        if not handled:
            raise cherrypy.HTTPError(404, "Unknown API route")
        return response

    def _entries_get(self, params):
        date = params.get("date") or datetime.date.today().isoformat()
        entries = list(self.time_keeper.data.get(date, []))
        entries.sort(key=lambda entry: entry.get("timestamp", ""))
        return {"date": date, "entries": entries}

    def _entries_post(self, payload):
        entry_type = self.time_keeper.parse_entry_type(payload.get("type"))
        date = payload.get("date") or datetime.date.today().isoformat()
        timestamp = parse_iso_datetime(payload.get("timestamp")) if payload.get("timestamp") else None

        entry = self.time_keeper.add_entry_at(date=date, entry_type=entry_type, timestamp=timestamp)
        self.time_keeper.save_data()
        cherrypy.response.status = 201
        return {"ok": True, "entry": entry}

    def _entries_patch(self, entry_id_raw, payload):
        try:
            entry_id = int(entry_id_raw)
        except (TypeError, ValueError) as e:
            raise cherrypy.HTTPError(400, "Entry id must be an integer") from e

        new_type = None
        if "type" in payload:
            new_type = self.time_keeper.parse_entry_type(payload.get("type"))

        new_timestamp = None
        if "timestamp" in payload:
            new_timestamp = parse_iso_datetime(payload.get("timestamp"))

        new_date = payload.get("date")

        if not self.time_keeper.entry_exists(entry_id):
            raise cherrypy.HTTPError(404, "Entry not found")

        self.time_keeper.edit_entry(
            entry_id=entry_id,
            new_type=new_type,
            new_timestamp=new_timestamp,
            new_date=new_date,
        )
        self.time_keeper.save_data()
        return {"ok": True}

    def _entries_delete(self, entry_id_raw):
        try:
            entry_id = int(entry_id_raw)
        except (TypeError, ValueError) as e:
            raise cherrypy.HTTPError(400, "Entry id must be an integer") from e

        if not self.time_keeper.entry_exists(entry_id):
            raise cherrypy.HTTPError(404, "Entry not found")

        self.time_keeper.delete_entry(entry_id)
        self.time_keeper.save_data()
        cherrypy.response.status = 204
        return None

    def _summary_get(self, params):
        date = params.get("date") or datetime.date.today().isoformat()
        worked = self.time_keeper.get_time_worked(date)
        target = self.config.get_daily_target()
        delta = duration_delta(worked, target)
        return {
            "date": date,
            "worked": worked,
            "target": target,
            "delta": delta,
            "weekly_delta": self.time_keeper.get_worked_delta_range(get_week_start(date).isoformat(), date, target),
            "total_delta": self.time_keeper.get_worked_delta_range(self.time_keeper.get_first_date() or date, date, target),
            "last_entry": self.time_keeper.get_last_entry(date),
        }

    def _history_get(self, params):
        raw_limit = params.get("limit", "14")
        last = params.get("last", None)
        try:
            limit = max(1, int(raw_limit))
        except ValueError as e:
            raise cherrypy.HTTPError(400, "limit must be an integer") from e

        dates = sorted(self.time_keeper.data.keys(), reverse=True)
        if last is not None:
            try:
                last_index = dates.index(str(last))
                dates = dates[:last_index]
            except ValueError:
                pass
        dates = dates[:limit]

        history = []
        for date in dates:
            worked = self.time_keeper.get_time_worked(date)
            target = self.config.get_daily_target()
            history.append(
                {
                    "date": date,
                    "worked": worked,
                    "delta": duration_delta(worked, target),
                }
            )
        return {"history": history, "full_length": len(self.time_keeper.data)}

    def _attendance_get(self):
        return {"records": self.attendance.records}

    def _attendance_post(self, params):
        date = params.get("date")
        status = params.get("status")
        self.attendance.add_record(date, status)
        return {"ok": True}

    def _read_json_body(self, required=False):
        raw_body = cherrypy.request.body.read()
        if not raw_body:
            if required:
                raise cherrypy.HTTPError(400, "Missing JSON body")
            return {}
        try:
            return json.loads(raw_body.decode("utf-8"))
        except Exception as exc:
            raise cherrypy.HTTPError(400, f"Invalid JSON body: {exc}")


if __name__ == "__main__":
    cherrypy.config.update(
        {
            "server.socket_host": "0.0.0.0",
            "server.socket_port": 8080,
            "tools.staticdir.root": APP_ROOT,
        }
    )

    app_config = {
        "/": {
            "tools.sessions.on": True,
            "tools.sessions.timeout": 60,
            "tools.sessions.secure": False,
            "tools.sessions.httponly": True,
            "tools.staticdir.on": True,
            "tools.staticdir.dir": "static/app",
            "tools.staticdir.index": "index.html",
            "tools.staticdir.match": r"^/$",
        },
        "/static": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": "static/",
            "tools.staticdir.match": r"^/static(?:/|$)",
            "tools.staticdir.index": "index.html",
        },
    }

    cherrypy.quickstart(TimeIt(), "", app_config)
