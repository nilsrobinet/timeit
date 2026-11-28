"""Main app for TimeIt. Contains the API."""

import os
import datetime
import json
from typing import Any, Callable

import cherrypy
from src.time_keeper import Attendance, TimeKeeper, EntryType
from src.time_util import duration_delta, parse_iso_datetime, seconds_to_duration, get_workday_dates
from src.config_handler import ConfigHandler

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

ROUTES: dict[tuple[str, str], Callable] = {}


def route(path: str, method: str):
    """Decorator for quickly defininge new api routes"""

    def decorator(func: Callable):
        ROUTES[(path, method.upper())] = func

    return decorator


class TimeIt(object):
    """TimeIt cherrypy web app."""

    def __init__(self, config_handler):
        self.config = config_handler
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

        path = "/".join(vpath)
        method = cherrypy.request.method.upper()

        handler = ROUTES.get((path, method))
        if not handler:
            raise cherrypy.HTTPError(404, f"Api route not found for route {path} with method {method}")

        return handler(self, params)

    @route("routes", "GET")
    def _routes_get(self, _params):
        return [{"route": t[0], "method": t[1]} for t in ROUTES.keys()]

    @route("day", "GET")
    def _day_get(self, params):
        date = params.get("date") or datetime.date.today().isoformat()
        day = self.time_keeper.get_day(date)
        return day.to_dict()

    @route("day/entry", "POST")
    def _day_entry_post(self, _params):
        payload = self._read_json_body(required=True)
        entry_type = EntryType(payload.get("type"))
        date = payload.get("date") or datetime.date.today().isoformat()
        timestamp = parse_iso_datetime(payload.get("timestamp")) if payload.get("timestamp") else None

        entry = self.time_keeper.add_entry_at(date=date, entry_type=entry_type, timestamp=timestamp)
        self.time_keeper.save_data()
        cherrypy.response.status = 201
        return {"ok": True, "entry": entry}

    @route("day/attendance", "POST")
    def _day_attendance_post(self, _param):
        payload = self._read_json_body(required=True)
        date = payload.get("date") or datetime.date.today().isoformat()
        status = Attendance(payload.get("status"))
        self.time_keeper.add_attendance(date=date, status=status)
        self.time_keeper.save_data()
        return {"ok": True}

    @route("day", "PATCH")
    def _day_patch(self, params):
        payload = self._read_json_body(required=True)
        entry_id = params.get("id")
        try:
            entry_id = int(entry_id)
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

    @route("day", "DELETE")
    def _day_delete(self, params):
        entry_id = params.get("id")
        date = params.get("date")
        try:
            entry_id = int(entry_id)
        except (TypeError, ValueError) as e:
            raise cherrypy.HTTPError(400, "Entry id must be an integer") from e

        day = self.time_keeper.get_day(date)
        if not day.get_entry(entry_id):
            raise cherrypy.HTTPError(404, f"Entry not found {date} {day.to_dict()} id {entry_id}")

        day.delete_entry(entry_id)
        self.time_keeper.save_data()
        cherrypy.response.status = 204
        return None

    @route("days", "GET")
    def _days_get(self, params):
        from_day = params.get("from", None)
        try:
            limit = int(params.get("limit", "14"))
        except ValueError as e:
            raise cherrypy.HTTPError(400, "limit must be an integer") from e

        history = [d.to_dict() for d in self.time_keeper.get_days(from_day, limit)]

        return {"history": history, "full_length": len(self.time_keeper.data) - 1}

    @route("days/summary", "GET")
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
        return {"history": history, "full_length": len(self.time_keeper.data) - 1}

    @route("days/attendance/avg", "GET")
    def _days_attendance_avg_get(self, params):
        total = self.time_keeper.total_attendance(Attendance(params.get("type")), params.get("date", datetime.date.today().isoformat()))
        workdays = len(get_workday_dates(self.config.get_workdays(), self.time_keeper.get_first_day().get_date(), params.get("date", datetime.date.today().isoformat())))
        return {total / workdays if workdays else 0}

    @route("days/attendance/target", "GET")
    def _days_attendance_target_get(self, _params):
        return {self.config.get_daily_target()}

    @route("days/attendance/total", "GET")
    def _days_attendance_total_get(self, params):
        return self.time_keeper.total_attendance(Attendance(params.get("type")), params.get("date", datetime.date.today().isoformat()))

    @route("summary", "GET")
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
            "avg_attendance": self.time_keeper.get_weighted_avg_attendance(self.config, date),
        }

    @route("report", "GET")
    def _report_get(self, _params):
        return self.time_keeper.generate_report(isLocal=True)

    @route("config", "GET")
    def _config_get(self, _params):
        return self.config.get_config()

    @route("config", "POST")
    def _config_target_post(self, _params):
        body = self._read_json_body(required=True)
        err = self.config.set_config(body)
        if err:
            raise cherrypy.HTTPError(400, str(err))
        return {"ok": True}

    @route("data", "GET")
    def _data_get(self, _params):
        """Export data"""
        return self.time_keeper.to_dict()

    @route("data", "POST")
    def _data_post(self, _params):
        body = self._read_json_body(required=True)
        self.time_keeper.from_dict(body)
        self.time_keeper.save_data()
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


class Server:
    """Server class handling configuration, setup and start."""

    def __init__(self):
        self.config = ConfigHandler(os.path.join(APP_ROOT, "config/userconf.yaml"), [self._update_callback])
        self.config.load()

        cherrypy.config.update(
            {
                "server.socket_host": "0.0.0.0",
                "server.socket_port": self.config.get_server_port(),
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

        cherrypy.quickstart(TimeIt(self.config), "", app_config)

    def _update_callback(self, updated_keys):
        if "server" in updated_keys:
            print("Server config updated")
            cherrypy.config.update({"server.socket_port": self.config.get_server_port()})
        cherrypy.engine.restart()


if __name__ == "__main__":
    Server()
