import os
import datetime
import json
import cherrypy
from src.TimeIt import TimeIt as TimeItData, EntryType

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

class TimeIt(object):

    def __init__(self):
        self.data = TimeItData(os.path.join(APP_ROOT, "data.json"))
        self.data.load_data()
    
    @cherrypy.expose
    def index(self):
        template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
        with open(template_path, encoding="utf-8") as template_file:
            return template_file.read()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def api(self, *vpath, **params):
        self.data.reload_if_changed()
        method = cherrypy.request.method.upper()

        if not vpath:
            raise cherrypy.HTTPError(404, "Missing API resource")

        resource = vpath[0]
        if resource == "entries":
            if method == "GET" and len(vpath) == 1:
                return self._entries_get(params)
            if method == "POST" and len(vpath) == 1:
                payload = self._read_json_body(required=True)
                return self._entries_post(payload)
            if method == "PATCH" and len(vpath) == 2:
                payload = self._read_json_body(required=True)
                return self._entries_patch(vpath[1], payload)
            if method == "DELETE" and len(vpath) == 2:
                return self._entries_delete(vpath[1])

        if resource == "summary" and method == "GET":
            return self._summary_get(params)

        if resource == "history" and method == "GET":
            return self._history_get(params)

        raise cherrypy.HTTPError(404, "Unknown API route")

    def _entries_get(self, params):
        date = params.get("date") or datetime.date.today().isoformat()
        entries = list(self.data.data.get(date, []))
        entries.sort(key=lambda entry: entry.get("timestamp", ""))
        return {"date": date, "entries": entries}

    def _entries_post(self, payload):
        entry_type = self._parse_entry_type(payload.get("type"))
        date = payload.get("date") or datetime.date.today().isoformat()
        timestamp = self._parse_iso_datetime(payload.get("timestamp")) if payload.get("timestamp") else None

        entry = self.data.add_entry_at(date=date, entry_type=entry_type, timestamp=timestamp)
        self.data.save_data()
        cherrypy.response.status = 201
        return {"ok": True, "entry": entry}

    def _entries_patch(self, entry_id_raw, payload):
        try:
            entry_id = int(entry_id_raw)
        except (TypeError, ValueError):
            raise cherrypy.HTTPError(400, "Entry id must be an integer")

        new_type = None
        if "type" in payload:
            new_type = self._parse_entry_type(payload.get("type"))

        new_timestamp = None
        if "timestamp" in payload:
            new_timestamp = self._parse_iso_datetime(payload.get("timestamp"))

        new_date = payload.get("date")

        updated = self._entry_exists(entry_id)
        if not updated:
            raise cherrypy.HTTPError(404, "Entry not found")

        self.data.edit_entry(
            entry_id=entry_id,
            new_type=new_type,
            new_timestamp=new_timestamp,
            new_date=new_date,
        )
        self.data.save_data()
        return {"ok": True}

    def _entries_delete(self, entry_id_raw):
        try:
            entry_id = int(entry_id_raw)
        except (TypeError, ValueError):
            raise cherrypy.HTTPError(400, "Entry id must be an integer")

        if not self._entry_exists(entry_id):
            raise cherrypy.HTTPError(404, "Entry not found")

        self.data.delete_entry(entry_id)
        self.data.save_data()
        cherrypy.response.status = 204
        return None

    def _summary_get(self, params):
        date = params.get("date") or datetime.date.today().isoformat()
        worked = self.data.get_time_worked(date)
        target = "8:00:00"
        delta = self._duration_delta(worked, target)
        return {
            "date": date,
            "worked": worked,
            "target": target,
            "delta": delta,
            "last_entry": self.data.get_last_entry(date),
        }

    def _history_get(self, params):
        raw_limit = params.get("limit", "14")
        try:
            limit = max(1, int(raw_limit))
        except ValueError:
            raise cherrypy.HTTPError(400, "limit must be an integer")

        dates = sorted(self.data.data.keys(), reverse=True)[:limit]
        history = []
        for date in dates:
            worked = self.data.get_time_worked(date)
            target = "8:00:00"
            history.append({
                "date": date,
                "worked": worked,
                "delta": self._duration_delta(worked, target),
            })
        return {"history": history}

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

    def _parse_entry_type(self, value):
        if value is None:
            return EntryType.AGNOSTIC
        try:
            return EntryType(str(value).lower())
        except ValueError:
            allowed = ", ".join(item.value for item in EntryType)
            raise cherrypy.HTTPError(400, f"Invalid type '{value}'. Use one of: {allowed}")

    def _parse_iso_datetime(self, value):
        if value is None:
            return None
        normalized = str(value).replace("Z", "+00:00")
        try:
            return datetime.datetime.fromisoformat(normalized)
        except ValueError:
            raise cherrypy.HTTPError(400, "timestamp must be ISO-8601")

    def _entry_exists(self, entry_id):
        for entries in self.data.data.values():
            for entry in entries:
                if int(entry.get("id", -1)) == entry_id:
                    return True
        return False

    def _duration_delta(self, worked, target):
        worked_seconds = self._duration_to_seconds(worked)
        target_seconds = self._duration_to_seconds(target)
        diff = worked_seconds - target_seconds
        sign = "+" if diff >= 0 else "-"
        return f"{sign}{self._seconds_to_duration(abs(diff))}"

    def _duration_to_seconds(self, duration):
        text = str(duration).strip()
        day_count = 0
        time_part = text

        if "day" in text:
            day_text, time_part = text.split(",", 1)
            day_count = int(day_text.split()[0])
            time_part = time_part.strip()

        parts = time_part.split(":")
        if len(parts) != 3:
            raise cherrypy.HTTPError(400, f"Invalid duration format: {duration}")

        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(float(parts[2]))
        hours += day_count * 24
        return (hours * 3600) + (minutes * 60) + seconds

    def _seconds_to_duration(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:01d}:{minutes:02d}:{seconds:02d}"
    
    
    
    
    
    
if __name__ == "__main__":
    cherrypy.config.update({
        "server.socket_host": "0.0.0.0",
        "server.socket_port": 8080,
    })

    app_config = {
        "/": {
            "tools.sessions.on": True,
            "tools.sessions.timeout": 60,
            "tools.sessions.secure": True,
            "tools.sessions.httponly": True,
        },
        "/static": {
            "tools.staticdir.on": True,
            "tools.staticdir.root": APP_ROOT,
            "tools.staticdir.dir": "static",
        },
    }

    cherrypy.quickstart(TimeIt(), "", app_config)
