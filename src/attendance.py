"""Attendance tracking."""

import os
import json


class Attendance:
    """Manage attendance records."""

    def __init__(self, attendance_path):
        self.attendance_path = attendance_path
        self.records = {}
        self.last_loaded_mtime_ns = None
        self.reload_if_changed()

    def load_attendance(self) -> dict:
        """Load attendance from file.
        :returns: Attendance dict in the form {date: {status: str}}
        """
        if os.path.exists(self.attendance_path):
            with open(self.attendance_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return dict()

    def save_attendance(self):
        """Save attendance to file."""
        with open(self.attendance_path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=4)

    def reload_if_changed(self) -> bool:
        """Reload if file changed.
        :returns: True if reloaded.
        """
        if not os.path.exists(self.attendance_path):
            if self.last_loaded_mtime_ns is not None or self.records:
                self.records = {}
                self.last_loaded_mtime_ns = None
            return False

        current_mtime_ns = os.stat(self.attendance_path).st_mtime_ns
        if self.last_loaded_mtime_ns == current_mtime_ns:
            return False

        self.records = self.load_attendance()
        self.last_loaded_mtime_ns = current_mtime_ns
        return True

    def add_record(self, date: str, status: str) -> None:
        """Add a new attendance record.
        :param date: Date of the record.
        :param status: Attendance status.
        """
        self.records[date] = {"status": status}
        self.save_attendance()
