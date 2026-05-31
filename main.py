import os
import cherrypy
from string import Template
from uuid import uuid4


class TimeIt(object):
    @cherrypy.expose
    def index(self):
        current_rows = [
            {"type": "Check In", "time": "09:00", "uuid": uuid4()},
            {"type": "Break", "time": "12:00", "uuid": uuid4()},
        ]
        history_rows = [
            {"date": "2026-05-30", "time": "08:45", "delta": "+00:15"},
            {"date": "2026-05-29", "time": "09:00", "delta": "-00:05"},
        ]

        current_rows_html = self._render_rows_today(current_rows)
        history_rows_html = self._render_rows_history(history_rows)

        template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
        with open(template_path, encoding="utf-8") as template_file:
            template = Template(template_file.read())

        return template.safe_substitute(
            timer="0:00:00",
            target="0:00:00",
            current_rows=current_rows_html,
            history_rows=history_rows_html,
        )

    def _render_rows_today(self, rows):
        return "\n".join(
            "<tr>" + 
            f"<td>{row.get("type", "")}</td>" +
            f"<td>{row.get("time", "")}</td>" +
            '<td><button type="button" class="btn btn-secondary btn-sm">Edit </button><td>' +
            "</tr>"
            for row in rows
        )
    
    def _render_rows_history(self, rows):
        keys = ('date', 'time', 'delta')
        return "\n".join(
            '<tr>' +
            ''.join([f'<td>{row.get(key, "")}</td>' for key in keys]) +
            '</tr>'
            for row in rows
        )
    
    
    
    
    
    
if __name__ == "__main__":
    cherrypy.quickstart(TimeIt(), "", "config/app.conf")
