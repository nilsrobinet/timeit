import datetime
import enum
import os

from flask import json

class EntryType(enum.Enum):
    START = "start"
    STOP = "stop"
    AGNOSTIC = "agnostic"

class TimeIt:

    def __init__(self):
        self.data: dict[str, list[dict]] = {}
        self.current_entry_id = 0

    def load_data(self):
        if not os.path.exists("data.json"):
            self.data = {}
            return
        with open("data.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)
    
    def save_data(self):
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def add_entry(self, entry_type=EntryType.AGNOSTIC):
        today = datetime.date.today().isoformat()
        if today not in self.data:
            self.data[today] = []
        self.data[today].append({"type": entry_type.value, "timestamp": datetime.datetime.now().isoformat(), "id": self.current_entry_id})
        self.current_entry_id += 1

    def edit_entry(self, entry_id, new_type=None, new_timestamp=None, new_date=None):
        for date, entries in self.data.items():
            for entry in entries:
                if entry["id"] == entry_id:
                    if new_type is not None:
                        entry["type"] = new_type.value
                    if new_timestamp is not None:
                        entry["timestamp"] = new_timestamp.isoformat()
                    if new_date is not None:
                        self.data[new_date] = self.data.pop(date)
                    return

    def delete_entry(self, entry_id):
        for date, entries in self.data.items():
            for i, entry in enumerate(entries):
                if entry["id"] == entry_id:
                    del entries[i]
                    return

    def get_time_worked(self, date=datetime.date.today().isoformat()):
        if date not in self.data:
            return "0:00:00"
        entries = self.data[date]
        total_seconds = 0
        for i in range(0, len(entries), 2):
            start_time = datetime.datetime.fromisoformat(entries[i]["timestamp"])
            stop_time = datetime.datetime.fromisoformat(entries[i + 1]["timestamp"])
            total_seconds += (stop_time - start_time).total_seconds()
        return str(datetime.timedelta(seconds=total_seconds))

    def get_last_entry(self, date=datetime.date.today().isoformat()):
        if date not in self.data or not self.data[date]:
            return None
        return self.data[date][-1]

if __name__ == "__main__":
    timeit = TimeIt()
    timeit.load_data()
    timeit.add_entry(EntryType.START)
    timeit.add_entry(EntryType.STOP)
    print(timeit.get_time_worked())
    print(timeit.get_last_entry())
    timeit.save_data()