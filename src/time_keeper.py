"""Time keeping classes. Can be used standalone for checking the database for inconsistencies."""

import datetime
import enum
import json
import os
import sys
from typing import TypeVar

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.time_util import as_utc, get_week_start, duration_to_seconds, get_workday_dates

UTC = datetime.UTC
EnumT = TypeVar("EnumT", bound=enum.Enum)


class Attendance(enum.Enum):
    """Attendance types."""

    IN_OFFICE = "in_office"
    REMOTE = "remote"
    VACATION = "vacation"
    SICK = "sick"
    UNDEFINED = "undefined"


class EntryType(enum.Enum):
    """Types of entries."""

    START = "start"
    STOP = "stop"
    AGNOSTIC = "agnostic"


def _enum_from_json(enum_type: type[EnumT], value: str) -> EnumT:
    try:
        return enum_type(value)
    except ValueError:
        return enum_type[value.upper()]


class Entry:
    """A time entry within a day."""

    def __init__(self, e_type: EntryType, timestamp: datetime.datetime | None, e_id: int):
        """Init entry.
        :param type: Entry type
        :param timestamp: Timestamp
        :param id: Entry ID
        """
        self.type = e_type
        self.timestamp: datetime.datetime = as_utc(timestamp or datetime.datetime.now(UTC))
        self.id = e_id

    def edit(self, new_type: EntryType | None, new_timestamp: datetime.datetime | None) -> None:
        """Edit entry.
        :param new_type: New type
        :param new_timestamp: New timestamp
        """
        if new_type is not None:
            self.type = new_type
        if new_timestamp is not None:
            self.timestamp = as_utc(new_timestamp)

    def get_timestamp(self) -> datetime.datetime:
        """Get timestamp.
        :returns: Timestamp
        """
        return self.timestamp

    def get_type(self) -> EntryType:
        """Get type.
        :returns: Entry type
        """
        return self.type

    def to_dict(self) -> dict:
        """Convert to dict.
        :returns: Dict
        """
        return {"type": self.type.value, "timestamp": self.timestamp.isoformat(), "id": self.id}

    @classmethod
    def from_dict(cls, data: dict) -> "Entry":
        """Create an entry from its serialized dictionary.
        :param data: Dict
        :returns: Entry
        """
        timestamp = data["timestamp"]
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.fromisoformat(timestamp)
        if not isinstance(timestamp, datetime.datetime):
            raise TypeError("Entry timestamp must be an ISO-8601 string or datetime")
        return cls(_enum_from_json(EntryType, data["type"]), timestamp, data["id"])


class Day:
    """A day with entries."""

    def __init__(self, date: str, attendance: Attendance):
        self.date = date
        self.attendance = attendance
        self.entries: list[Entry] = []

    def set_attendance(self, status: str | Attendance):
        """Set attendance."""
        if isinstance(status, Attendance):
            self.attendance = status
        else:
            status = status.upper()
            self.attendance = _enum_from_json(Attendance, status)

    def get_date(self) -> str:
        """Get date.
        :returns: Date
        """
        return self.date

    def get_attendance(self) -> Attendance:
        """Get attendance.
        :returns: Attendance
        """
        return self.attendance

    def add_entry(self, entry: Entry):
        """Add entry.
        :param entry: Entry to add
        """
        self.entries.append(entry)
        self.entries.sort(key=lambda e: e.timestamp)

    def get_entry(self, e_id: int) -> Entry | None:
        """Get entry by ID.
        :param e_id: Entry ID
        :returns: Entry or None
        """
        for e in self.entries:
            if e.id == e_id:
                return e
        return None

    def delete_entry(self, e_id: int):
        """Delete entry by ID.
        :param e_id: Entry ID
        """
        self.entries = [e for e in self.entries if e.id != e_id]

    def to_dict(self) -> dict:
        """Convert to dict.
        :returns: Dict
        """
        return {"date": self.date, "attendance": self.attendance.value, "entries": [e.to_dict() for e in self.entries]}

    @classmethod
    def from_dict(cls, data: dict, date: str | None = None) -> "Day":
        """Create a day from its serialized dictionary.
        :param data: Dict
        :param date: Optional date
        :returns: Day
        """
        day_date = data.get("date", date)
        if day_date is None:
            raise ValueError("Day date is required")
        attendance = data.get("attendance", Attendance.UNDEFINED.value)
        day = cls(day_date, _enum_from_json(Attendance, attendance))
        for entry in data.get("entries", []):
            day.add_entry(Entry.from_dict(entry))
        return day

    def get_time_worked(self) -> datetime.timedelta:
        """Get time worked.
        :returns: timedelta
        """
        worked = datetime.timedelta()
        for i in range(0, len(self.entries), 2):
            if i + 1 >= len(self.entries):
                break
            if self.entries[i].type != EntryType.START:
                raise ValueError("Expected START entry")
            if self.entries[i + 1].type != EntryType.STOP:
                raise ValueError("Expected STOP entry")
            if i + 1 < len(self.entries):
                worked += self.entries[i + 1].timestamp - self.entries[i].timestamp
        return worked

    def get_newest_entry(self) -> Entry | None:
        """Get newest entry.
        :returns: Entry or None
        """
        return self.entries[-1] if self.entries else None

    def check_consistency(self):
        """Check day consistency."""
        self.entries.sort(key=lambda e: e.timestamp)
        for i in range(1, len(self.entries)):
            if self.entries[i].type == self.entries[i - 1].type:
                raise ValueError("Inconsistent entries")


class TimeKeeper:
    """Manage time entries."""

    def __init__(self, data_path="data.json") -> None:
        self.data_path = data_path
        self.data: dict[str, Day] = {}
        self.current_entry_id = 0
        self.last_loaded_mtime_ns: int | None = None

    def load_data(self):
        """Load data from file."""
        if not os.path.exists(self.data_path):
            self.data = {}
            self.current_entry_id = 0
            self.last_loaded_mtime_ns = None
            return
        with open(self.data_path, "r", encoding="utf-8") as f:
            serialized_data = json.load(f)
        self.data = {date: Day.from_dict(day, date) for date, day in serialized_data.items()}
        self.current_entry_id = self._get_next_id()
        self.last_loaded_mtime_ns = os.stat(self.data_path).st_mtime_ns

    def reload_if_changed(self) -> bool:
        """Reload if file changed.
        :returns: True if reloaded
        """
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
        """Save data to file."""
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump({date: day.to_dict() for date, day in self.data.items()}, f, indent=4)
        self.last_loaded_mtime_ns = os.stat(self.data_path).st_mtime_ns

    def add_entry(self, entry_type: EntryType = EntryType.AGNOSTIC):
        """Add entry for today.
        :param entry_type: Type of entry
        """
        today = datetime.date.today().isoformat()
        self.add_entry_at(today, entry_type)

    def add_entry_at(
        self,
        date: str,
        entry_type: EntryType = EntryType.AGNOSTIC,
        timestamp: datetime.datetime | None = None,
    ) -> dict:
        """Add entry at specific date.
        :param date: Date for the entry
        :param entry_type: Type of entry
        :param timestamp: Optional timestamp for the entry
        :returns: the added entry
        """
        if date not in self.data:
            self.data[date] = Day(date, Attendance.UNDEFINED)
        entry = Entry(entry_type, timestamp, self.current_entry_id)

        self.data[date].add_entry(entry)
        self.current_entry_id += 1
        return entry.to_dict()

    def edit_entry(
        self,
        entry_id: int,
        date: str,
        new_type: EntryType | None = None,
        new_timestamp: datetime.datetime | None = None,
    ) -> None:
        """Edit an existing entry.
        :param date: Date of the entry
        :param entry_id: ID of the entry
        :param new_type: New type if changing
        :param new_timestamp: New timestamp if changing
        """
        if date:
            entry = self.data.get(date, Day(date, Attendance.UNDEFINED)).get_entry(entry_id)
            if entry:
                entry.edit(new_type, new_timestamp)
        else:
            for day in self.data.values():
                entry = day.get_entry(entry_id)
                if entry:
                    entry.edit(new_type, new_timestamp)

    def delete_entry(self, entry_id: int, date: str | None = None):
        """Delete an entry.
        :param entry_id: ID of the entry
        :param date: Optional date of the entry TODO: make mandatory
        """
        if not self.data:
            return

        if date:
            self.data.get(date, Day(date, Attendance.UNDEFINED)).delete_entry(entry_id)
        else:
            for day in self.data.values():
                day.delete_entry(entry_id)

    def get_day(self, date: str) -> Day:
        """Get a day by date, returns empty if not found
        :param date: Date string
        :returns: Day object
        """
        return self.data.get(date, Day(date, Attendance.UNDEFINED))

    def get_first_day(self) -> Day:
        """Get first day in data"""
        return self.data[min(self.data.keys())] if self.data else Day("", Attendance.UNDEFINED)

    def get_weighted_avg_attendance(self, config, date: str) -> float:
        """Get weighted avg attendance with vacation and sick days counting for half"""
        total = self.total_attendance(Attendance.UNDEFINED, date)
        vacation = self.total_attendance(Attendance.VACATION, date)
        sick = self.total_attendance(Attendance.SICK, date)
        workdays = len(get_workday_dates(config.get_workdays(), self.get_first_day().get_date(), date))
        return (total + (vacation / 2) + (sick / 2)) / workdays if workdays else 0

    def get_days(self, from_day: str | None = None, limit: int = 14) -> list[Day]:
        """Get days from from_day, limited by limit
        :param from_day: start date
        :param limit: max number of days
        :returns: list of days
        """
        dates = [datetime.date.fromisoformat(d) for d in sorted(self.data.keys(), reverse=True)]
        if from_day:
            dates = [d for d in dates if d < datetime.date.fromisoformat(from_day)]
        return [self.data[d.isoformat()] for d in dates[:limit]]

    def get_worked_weekly(self, date: str, target: str) -> datetime.timedelta:
        """Get worked time for the week
        :param date: any date in the week
        :param target: daily target
        :returns: timedelta
        """
        start = get_week_start(date).isoformat()
        worked = datetime.timedelta()
        for d in self.data:
            if start <= d <= date:
                worked += self.data[d].get_time_worked()

        target_dt = datetime.timedelta(seconds=duration_to_seconds(target))
        worked -= target_dt

        return worked

    def get_worked_delta(self, date: str, target: str) -> datetime.timedelta:
        """Get worked delta for all days up to date
        :param date: end date
        :param target: daily target
        :returns: timedelta
        """
        worked = datetime.timedelta()
        days = [d for d in self.data if d <= date]
        for d in days:
            worked += self.data[d].get_time_worked()
        return worked - datetime.timedelta(seconds=duration_to_seconds(target) * len(days))

    def _get_next_id(self):
        max_id = 0
        for day in self.data.values():
            for entry in day.entries:
                max_id = max(max_id, entry.id)
        return max_id + 1

    def total_attendance(self, attandance_type: Attendance, date: str) -> int:
        """Count attendance of type up to date
        :param attandance_type: type to count
        :param date: up to this date
        :returns: count
        """
        days = [d for d in self.data if d <= date]
        return sum(1 for d in days if self.data[d].attendance == attandance_type)

    def generate_report(self, isLocal: bool = False) -> list[str]:  # pylint: disable=missing-param-doc,missing-return-doc
        """Generate report containing inconsistent days, missing attendance and other issues"""
        sorted_data = sorted(self.data)
        errors: list[str] = []
        for d in sorted_data:
            try:
                self.data[d].check_consistency()
            except ValueError:
                errors.append(f"Inconsistent entries {d}")
            if self.data[d].attendance is None or self.data[d].attendance == Attendance.UNDEFINED and d <= datetime.date.today().isoformat():
                errors.append(f"Missing attendance {d}")

            workdays = ["MON", "TUE", "WED", "THU", "FRI"]
        wdays: list[datetime.date] = get_workday_dates(workdays, sorted_data[0], sorted_data[-1])

        for wd in wdays:
            if wd.isoformat() not in self.data:
                errors.append(f"Missing workday {wd}")
        if isLocal:
            print(errors)
        return errors

    def to_dict(self):
        """Export data as dict"""
        return {d: self.data[d].to_dict() for d in self.data}

    def from_dict(self, data):
        for d in data:
            self.data[d] = Day.from_dict(data[d])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TimeIt CLI")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check the consistency of the time entries and generate a report for suspicious entries",
    )
    args = parser.parse_args()
    timeit = TimeKeeper()
    timeit.load_data()
    if args.check:
        timeit.generate_report(isLocal=True)
