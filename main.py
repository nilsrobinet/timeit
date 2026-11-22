"""Main app for TimeIt. Contains the API."""

import os
import datetime
import json
from typing import Any

import cherrypy
from src.time_keeper import TimeKeeper, EntryType
from src.time_util import duration_delta, parse_iso_datetime, seconds_to_duration
from src.config_handler import ConfigHandler

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


class TimeIt(object):
    """TimeIt cherrypy web app."""

    def __init__(self):
        self.config = ConfigHandler(os.path.join(APP_ROOT, "config/userconf.toml"))
        self.config.load()
        self.time_keeper = TimeKeeper(os.path.join(APP_ROOT, self.config.get_timekeeping_path()))
        self.time_keeper.load_data()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def api(self, *vpath, **params) -> dict[str, Any] | None:
        """Handle API requests.
        :param vpath: API resource path components.
        :param params: Query parameters for the request.
        :returns: The API response payload.
        """
        self.time_keeper.reload_if_changed()
        method = cherrypy.request.method.upper()

        if not vpath:
            raise cherrypy.HTTPError(404, "Missing API resource")

        resource = vpath[0]
        handled = True
        response = None
        if resource == "day":
            if method == "GET" and len(vpath) == 1:
                response = self._day_get(params)
            elif method == "POST":
                if len(vpath) == 2 and vpath[1] == "entry":
                    payload = self._read_json_body(required=True)
                    response = self._day_entry_post(payload)
                elif len(vpath) == 2 and vpath[1] == "attendance":
                    payload = self._read_json_body(required=True)
                    response = self._day_attendance_post(payload)
            elif method == "PATCH" and len(vpath) == 2:
                payload = self._read_json_body(required=True)
                response = self._day_patch(vpath[1], payload)
            elif method == "DELETE" and len(vpath) == 2:
                self._day_delete(vpath[1], params.get("date"))
            else:
                handled = False
        elif resource == "summary" and method == "GET":
            response = self._summary_get(params)
        elif resource == "days" and method == "GET":
            if len(vpath) == 1:
                response = self._days_get(params)
            elif len(vpath) == 2 and vpath[1] == "summary":
                response = self._days_summary_get(params)
        elif resource == "config" and method == "GET":
            response = self.config.get_config()
        else:
            handled = False

        if not handled:
            raise cherrypy.HTTPError(404, "Unknown API route")
        return response

    def _day_get(self, params):
        date = params.get("date") or datetime.date.today().isoformat()
        day = self.time_keeper.get_day(date)
        return day.to_dict()

    def _day_entry_post(self, payload):
        entry_type = EntryType(payload.get("type"))
        date = payload.get("date") or datetime.date.today().isoformat()
        timestamp = parse_iso_datetime(payload.get("timestamp")) if payload.get("timestamp") else None

        entry = self.time_keeper.add_entry_at(date=date, entry_type=entry_type, timestamp=timestamp)
        self.time_keeper.save_data()
        cherrypy.response.status = 201
        return {"ok": True, "entry": entry}

    def _day_attendance_post(self, payload):
        date = payload.get("date") or datetime.date.today().isoformat()
        status = payload.get("status")
        print(date, status)
        self.time_keeper.get_day(date).set_attendance(status)
        self.time_keeper.save_data()
        return {"ok": True}

    def _day_patch(self, entry_id_raw, payload):
        try:
            entry_id = int(entry_id_raw)
        except (TypeError, ValueError) as e:
            raise cherrypy.HTTPError(400, "Entry id must be an integer") from e

        new_type = None
        if "type" in payload:
            new_type = EntryType(payload.get("type"))

        new_timestamp = None
        if "timestamp" in payload:
            new_timestamp = parse_iso_datetime(payload.get("timestamp"))

        date = payload.get("date")

        if not self.time_keeper.get_day(date).get_entry(entry_id):
            raise cherrypy.HTTPError(404, "Entry not found")

        self.time_keeper.edit_entry(
            date=date,
            entry_id=entry_id,
            new_type=new_type,
            new_timestamp=new_timestamp,
        )
        self.time_keeper.save_data()
        return {"ok": True}

    def _day_delete(self, entry_id_raw, date):
        try:
            entry_id = int(entry_id_raw)
        except (TypeError, ValueError) as e:
            raise cherrypy.HTTPError(400, "Entry id must be an integer") from e

        day = self.time_keeper.get_day(date)
        if not day.get_entry(entry_id):
            raise cherrypy.HTTPError(404, "Entry not found")

        day.delete_entry(entry_id)
        self.time_keeper.save_data()
        cherrypy.response.status = 204
        return None

    def _days_get(self, params):
        from_day = params.get("from", None)
        try:
            limit = int(params.get("limit", "14"))
        except ValueError as e:
            raise cherrypy.HTTPError(400, "limit must be an integer") from e

        history = [d.to_dict() for d in self.time_keeper.get_days(from_day, limit)]

        return {"history": history, "full_length": len(self.time_keeper.data)}

    def _days_summary_get(self, params):
        from_day = params.get("from", None)
        try:
            limit = int(params.get("limit", "14"))
        except ValueError as e:
            raise cherrypy.HTTPError(400, "limit must be an integer") from e

        history = [
            {
                "date": d.date,
                "worked": seconds_to_duration(int(d.get_time_worked().total_seconds())),
                "delta": duration_delta(seconds_to_duration(int(d.get_time_worked().total_seconds())), self.config.get_daily_target()),
                "attendance": d.get_attendance().value,
            }
            for d in self.time_keeper.get_days(from_day, limit)
        ]
        return {"history": history, "full_length": len(self.time_keeper.data)}

    def _summary_get(self, params):
        date = params.get("date") or datetime.date.today().isoformat()
        target = self.config.get_daily_target()

        try:
            worked = seconds_to_duration(int(self.time_keeper.get_day(date).get_time_worked().total_seconds()))
        except ValueError as e:
            raise cherrypy.HTTPError(500, str(e)) from e

        delta = duration_delta(worked, target)
        last_entry = self.time_keeper.get_day(date).get_newest_entry()
        return {
            "date": date,
            "worked": worked,
            "target": target,
            "delta": delta,
            "weekly_delta": seconds_to_duration(int(self.time_keeper.get_worked_weekly(date, target).total_seconds())),
            "total_delta": seconds_to_duration(int(self.time_keeper.get_worked_delta(date, target).total_seconds())),
            "last_entry": last_entry.to_dict() if last_entry else None,
        }

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
