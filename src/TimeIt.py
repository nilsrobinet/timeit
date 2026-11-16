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

    def get_first_date(self):
        if not self.data:
            return None
        return min(self.data.keys())

    def get_worked_delta_range(self, start_date, end_date, daily_target):
        print(f"Calculating worked delta from {start_date} to {end_date} with daily target {daily_target}")
        target_h, target_m , target_s = map(int, daily_target.split(":"))
        total_target_s = (target_h * 3600 + target_m * 60 + target_s) * self.get_number_of_dates_in_range(start_date, end_date)
        total_worked_s = self.get_time_worked_range_seconds(start_date, end_date)
        delta_seconds = total_worked_s - total_target_s
        sign = "-" if delta_seconds < 0 else ""
        hours, remainder = divmod(abs(delta_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        delta = f"{sign}{hours}:{minutes:02}:{seconds:02}"

        print(f"delta: {delta} with days worked: {self.get_number_of_dates_in_range(start_date, end_date)} ({total_worked_s} seconds worked {total_target_s} seconds target)")
        return delta

    def get_time_worked_range_seconds(self, start_date, end_date):
        total_seconds = 0.0
        if not isinstance(start_date, datetime.date):
            start_date = datetime.date.fromisoformat(start_date)
        current_date = start_date
        while current_date <= datetime.date.fromisoformat(end_date):
            total_seconds += self._get_time_worked_for_date(current_date)
            current_date += datetime.timedelta(days=1)
        return int(total_seconds)

    def get_number_of_dates_in_range(self, start_date, end_date):
        if not isinstance(start_date, datetime.date):
            start_date = datetime.date.fromisoformat(start_date)
        if not isinstance(end_date, datetime.date):
            end_date = datetime.date.fromisoformat(end_date)
        count = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.isoformat() in self.data:
                count += 1
            current_date += datetime.timedelta(days=1)
        return count

    def get_time_worked_range(self, start_date, end_date):
        total_seconds = self.get_time_worked_range_seconds(start_date, end_date)
        return str(datetime.timedelta(seconds=int(total_seconds)))

    def _get_time_worked_for_date(self, date):
        date_str = date.isoformat() if isinstance(date, datetime.date) else date
        if date_str not in self.data:
            return 0.0
        entries = self.data[date_str]
        entries = sorted(entries, key=lambda e: e["timestamp"])
        total_seconds = 0.0
        for i in range(0, len(entries) - 1, 2):
            start_time = datetime.datetime.fromisoformat(entries[i]["timestamp"])
            stop_time = datetime.datetime.fromisoformat(entries[i + 1]["timestamp"])
            total_seconds += (stop_time - start_time).total_seconds()
        return total_seconds
    
    def get_time_worked(self, date=datetime.date.today().isoformat()):
        total_seconds = self._get_time_worked_for_date(date)
        return str(datetime.timedelta(seconds=int(total_seconds)))

    def get_last_entry(self, date=datetime.date.today().isoformat()):
        if date not in self.data or not self.data[date]:
            return None
        self.data[date] = sorted(self.data[date], key=lambda e: e["timestamp"])
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

    def check_consistency(self):
        suspicious_entries = []
        for date, entries in self.data.items():
            entries = sorted(entries, key=lambda e: e["timestamp"])
            if not entries:
                suspicious_entries.append((date, entries, 'No entries for this date'))
                continue
            for i in range(0, len(entries) - 1, 2):
                start_time = datetime.datetime.fromisoformat(entries[i]["timestamp"])
                stop_time = datetime.datetime.fromisoformat(entries[i + 1]["timestamp"])
                if stop_time < start_time:
                    suspicious_entries.append((date, entries, f'Stop time {stop_time} is before start time {start_time}'))
            if len(entries) == 1:
                suspicious_entries.append((date, entries, 'Only one entry for this date'))
            if entries[-1]['type'] == 'start':
                suspicious_entries.append((date, entries, 'Last entry is a start entry without a corresponding stop'))
        return suspicious_entries

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TimeIt CLI")
    parser.add_argument("--check", action="store_true", help="Check the consistency of the time entries and generate a report for suspicious entries")
    args = parser.parse_args()
    timeit = TimeIt()
    timeit.load_data()
    if args.check:
        suspicious_entries = timeit.check_consistency()
        if suspicious_entries:
            print("Suspicious entries found:")
            for date, entries, reason in suspicious_entries:
                print(f"Date: {date}, Reason: {reason}")
                for entry in entries:
                    print(f"  {entry}")
        else:
            print("No suspicious entries found.")
