import json
import datetime
from enum import Enum
import os

class Attendance:

    def __init__(self, attendance_path):
        self.attendance_path = attendance_path
        self.records = {}
        self.last_loaded_mtime_ns = None
        self.reload_if_changed()

    def load_attendance(self):
        if os.path.exists(self.attendance_path):
            with open(self.attendance_path, 'r') as f:
                return json.load(f)
        return []

    def save_attendance(self):
        with open(self.attendance_path, 'w') as f:
            json.dump(self.records, f, indent=4)

    def reload_if_changed(self):
        if not os.path.exists(self.attendance_path):
            if self.last_loaded_mtime_ns is not None or self.records:
                self.records = []
                self.last_loaded_mtime_ns = None
            return False

        current_mtime_ns = os.stat(self.attendance_path).st_mtime_ns
        if self.last_loaded_mtime_ns == current_mtime_ns:
            return False

        self.records = self.load_attendance()
        self.last_loaded_mtime_ns = current_mtime_ns
        return True

    def add_record(self, date, status):
        self.records[date] = {
            'status': status
        }
        self.save_attendance()
