import datetime
import enum
import json
import os

UTC = datetime.UTC

class EntryType(enum.Enum):
    START = "start"
    STOP = "stop"
    AGNOSTIC = "agnostic"

class TimeIt:

    def __init__(self, data_path="data.json"):
        self.data_path = data_path
        self.data: dict[str, list[dict]] = {}
        self.current_entry_id = 0
        self.last_loaded_mtime_ns = None

    def load_data(self):
        if not os.path.exists(self.data_path):
            self.data = {}
            self.current_entry_id = 0
            self.last_loaded_mtime_ns = None
            return
        with open(self.data_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.current_entry_id = self._next_entry_id()
        self.last_loaded_mtime_ns = os.stat(self.data_path).st_mtime_ns

    def reload_if_changed(self):
        if not os.path.exists(self.data_path):
            if self.last_loaded_mtime_ns is not None or self.data:
                self.data = {}
                self.current_entry_id = 0
                self.last_loaded_mtime_ns = None
            return False

        current_mtime_ns = os.stat(self.data_path).st_mtime_ns
        if self.last_loaded_mtime_ns == current_mtime_ns:
            return False

        self.load_data()
        return True
    
    def save_data(self):
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
        self.last_loaded_mtime_ns = os.stat(self.data_path).st_mtime_ns

    def add_entry(self, entry_type=EntryType.AGNOSTIC):
        today = datetime.date.today().isoformat()
        if today not in self.data:
            self.data[today] = []
        self.data[today].append({
            "type": entry_type.value,
            "timestamp": datetime.datetime.now(UTC).isoformat(),
            "id": self.current_entry_id,
        })
        self.current_entry_id += 1

    def add_entry_at(self, date, entry_type=EntryType.AGNOSTIC, timestamp=None):
        if date not in self.data:
            self.data[date] = []
        entry = {
            "type": entry_type.value,
            "timestamp": self._as_utc(timestamp or datetime.datetime.now(UTC)).isoformat(),
            "id": self.current_entry_id,
        }
        self.data[date].append(entry)
        self.current_entry_id += 1
        return entry

    def edit_entry(self, entry_id, new_type=None, new_timestamp=None, new_date=None):
        for date, entries in list(self.data.items()):
            for entry in entries:
                if int(entry.get("id", -1)) == entry_id:
                    if new_type is not None:
                        entry["type"] = new_type.value
                    if new_timestamp is not None:
                        entry["timestamp"] = self._as_utc(new_timestamp).isoformat()
                    if new_date is not None and new_date != date:
                        if new_date not in self.data:
                            self.data[new_date] = []
                        self.data[new_date].append(entry)
                        entries.remove(entry)
                    return

    def delete_entry(self, entry_id):
        for date, entries in self.data.items():
            for i, entry in enumerate(entries):
                if int(entry.get("id", -1)) == entry_id:
                    del entries[i]
                    return

    def get_time_worked(self, date=datetime.date.today().isoformat()):
        if date not in self.data:
            return "0:00:00"
        entries = self.data[date]
        total_seconds = 0.0
        for i in range(0, len(entries) - 1, 2):
            start_time = datetime.datetime.fromisoformat(entries[i]["timestamp"])
            stop_time = datetime.datetime.fromisoformat(entries[i + 1]["timestamp"])
            total_seconds += (stop_time - start_time).total_seconds()
        return str(datetime.timedelta(seconds=int(total_seconds)))

    def get_last_entry(self, date=datetime.date.today().isoformat()):
        if date not in self.data or not self.data[date]:
            return None
        return self.data[date][-1]

    def _next_entry_id(self):
        max_id = -1
        for entries in self.data.values():
            for entry in entries:
                max_id = max(max_id, int(entry.get("id", -1)))
        return max_id + 1

    def _as_utc(self, value):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

if __name__ == "__main__":
    timeit = TimeIt()
    timeit.load_data()
    timeit.add_entry(EntryType.START)
    timeit.add_entry(EntryType.STOP)
    print(timeit.get_time_worked())
    print(timeit.get_last_entry())
    timeit.save_data()