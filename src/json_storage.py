"""JSON storage class for saving and loading data."""

import os
import json

from src.data_model import Day, Attendance
from src.storage import Storage


class JsonStorage(Storage):
    """JSON storage."""

    def __init__(self, file="data.json"):
        self.file = file
        self.current_entry_id = 0
        self.last_loaded_mtime_ns = None
        self.data: dict[str, Day] = {}
        self.load()

    def save(self):
        """Save data to file."""
        print("Saving data")
        self._clean()
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump({date: day.to_dict() for date, day in self.data.items()}, f, indent=4)
        self.last_loaded_mtime_ns = os.stat(self.file).st_mtime_ns

    def load(self):
        """Load data from file."""
        if not os.path.exists(self.file):
            self.data = {}
            self.current_entry_id = 0
            self.last_loaded_mtime_ns = None
            return
        with open(self.file, "r", encoding="utf-8") as f:
            serialized_data = json.load(f)
        self._clean()
        self.data = {date: Day.from_dict(day, date) for date, day in serialized_data.items()}
        self.current_entry_id = self.get_next_id()
        self.last_loaded_mtime_ns = os.stat(self.file).st_mtime_ns

    def get(self, date):
        self._reload_if_changed()
        return self.data.get(date)

    def get_or_create(self, date):
        self._reload_if_changed()
        if date not in self.data:
            self.data[date] = Day(date, Attendance.UNDEFINED)
        return self.data[date]

    def add(self, day: Day) -> None:
        self._reload_if_changed()
        self.data[day.date] = day
        self.save()

    def update(self, day: Day) -> None:
        self._reload_if_changed()
        self.data[day.date] = day
        self.save()

    def update_storage(self) -> None:
        self.save()

    def remove(self, date) -> None:
        self._reload_if_changed()
        self.data.pop(date, None)
        self.save()

    def has(self, date) -> bool:
        self._reload_if_changed()
        return date in self.data

    def get_next_id(self):
        max_id = 0
        for day in self.data.values():
            for entry in day.entries:
                max_id = max(max_id, entry.id)
        return max_id + 1

    def get_dates(self) -> list[str]:
        return list(self.data.keys())

    def _clean(self):
        self.data = dict(sorted(self.data.items()))
        for date in list(self.data.keys()):
            if not self.data[date].entries and self.data[date].attendance == Attendance.UNDEFINED:
                self.data.pop(date)

    def _reload_if_changed(self) -> bool:
        """Reload if file changed.
        :returns: True if reloaded
        """
        if not os.path.exists(self.file):
            if self.last_loaded_mtime_ns is not None or self.data:
                self.data = {}
                self.current_entry_id = 0
                self.last_loaded_mtime_ns = None
            return False

        current_mtime_ns = os.stat(self.file).st_mtime_ns
        if self.last_loaded_mtime_ns == current_mtime_ns:
            return False

        self.load()
        return True
