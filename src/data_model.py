"""
Module containing the class structure for the internal data model
"""

import enum
import datetime
from typing import TypeVar
from src.time_util import as_utc

UTC = datetime.UTC
EnumT = TypeVar("EnumT", bound=enum.Enum)


class Attendance(enum.Enum):
    """Attendance types."""

    IN_OFFICE = "in_office"
    REMOTE = "remote"
    VACATION = "vacation"
    SICK = "sick"
    PUBLIC_HOLIDAY = "public_holiday"
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

    def get_time_worked(self, time_sick, time_vac) -> datetime.timedelta:
        """Get time worked.
        :returns: timedelta
        """
        if self.attendance == Attendance.SICK:
            return time_sick
        if self.attendance == Attendance.VACATION:
            return time_vac
        worked = datetime.timedelta()
        for i in range(0, len(self.entries), 2):
            if i + 1 >= len(self.entries):
                break
            if self.entries[i].type != EntryType.START:
                raise ValueError(f"Expected START entry got: {self.entries[i].to_dict()}")
            if self.entries[i + 1].type != EntryType.STOP:
                raise ValueError(f"Expected STOP entry got: {self.entries[i].to_dict()}")
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
