"""Time keeping classes. Can be used standalone for checking the database for inconsistencies."""

import datetime

from src.storage import Storage
from src.data_model import Day, Entry, EntryType, Attendance
from src.time_util import get_week_start, duration_to_seconds, get_workday_dates


class TimeKeeper:
    """Manage time entries."""

    def __init__(self, persistance: Storage) -> None:
        self.storage = persistance
        self.last_loaded_mtime_ns: int | None = None

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
        entry = Entry(entry_type, timestamp, self.storage.get_next_id())

        day = self.storage.get_or_create(date)
        day.add_entry(entry)
        self.storage.update(day)
        return entry.to_dict()

    def edit_entry(
        self,
        entry_id: int,
        date: str,
        new_type: EntryType | None = None,
        new_timestamp: datetime.datetime | None = None,
    ) -> Day | None:
        """Edit an existing entry."""

        day = self.storage.get(date)
        if not day:
            return None
        entry = day.get_entry(entry_id)
        if entry:
            entry.edit(new_type, new_timestamp)
            self.storage.update(day)
        return day

    def delete_entry(self, date: str, entry_id: int) -> Day | None:
        """Delete an entry."""
        day = self.storage.get(date)
        if day:
            day.delete_entry(entry_id)
            self.storage.update(day)
        return day

    def add_attendance(self, date: str, status: Attendance):
        """Add attendance for a day"""
        print("Adding attendance", date, status)
        day = self.storage.get(date)
        if day:
            day.set_attendance(status)
        else:
            day = Day(date, status)
        self.storage.update(day)

    def get_day(self, date: str) -> Day:
        """Get a day by date, returns empty if not found
        NOTE: This getter is strictly read only any changes to the returned day won't be saved
        """
        day = self.storage.get_or_create(date)
        return day

    def get_first_day(self) -> Day | None:
        """Get first day in data"""
        return self.storage.get(min(self.storage.get_dates()))

    def get_days(self, from_day: str | None = None, limit: int = 14) -> list[Day | None]:
        """Get days from from_day, limited by limit
        NOTE: This getter is strictly read only any changes to the returned days won't be saved
        """
        dates = [datetime.date.fromisoformat(d) for d in sorted(self.storage.get_dates(), reverse=True)]
        if from_day:
            dates = [d for d in dates if d < datetime.date.fromisoformat(from_day)]
        return [self.storage.get(d.isoformat()) for d in dates[:limit]]

    def get_avg_attendance(self, workdays: list[str], sick_comp: float, vac_comp: float, date: str) -> float:
        """Get weighted avg attendance with vacation and sick days counting for half"""
        worked = self.total_attendance(Attendance.IN_OFFICE, date)
        vacation = self.total_attendance(Attendance.VACATION, date)
        sick = self.total_attendance(Attendance.SICK, date)
        first_day = self.get_first_day()
        if not first_day:
            return 0
        num_workdays = len(get_workday_dates(workdays, first_day.get_date(), date))
        total = worked + (vacation * vac_comp) + (sick * sick_comp)
        print(total, num_workdays, date)
        return (total) / num_workdays if num_workdays else 0

    def get_avg_attendance_days(self, workdays: list[str], sick_comp: float, vac_comp: float, date: str) -> float:
        """Get avg attendance in terms of days per week"""
        return self.get_avg_attendance(workdays, sick_comp, vac_comp, date) * len(workdays)

    def get_worked_weekly(self, date: str, target: str, sick_time: datetime.timedelta, vac_time: datetime.timedelta) -> datetime.timedelta:
        """Get worked time for the week"""
        start = get_week_start(date).isoformat()
        worked = datetime.timedelta()
        for d in self.storage.get_dates():
            day = self.storage.get(d)
            if not day:
                continue
            if start <= d <= date:
                worked += day.get_time_worked(sick_time, vac_time)

        target_dt = datetime.timedelta(seconds=duration_to_seconds(target))
        worked -= target_dt

        return worked

    def get_worked_delta(self, date: str, target: str, sick_time: datetime.timedelta, vac_time: datetime.timedelta) -> datetime.timedelta:
        """Get worked delta for all days up to date"""
        worked = datetime.timedelta()
        days = [d for d in self.storage.get_dates() if d <= date]
        for d in days:
            day = self.storage.get(d)
            if not day:
                continue
            worked += day.get_time_worked(sick_time, vac_time)
        return worked - datetime.timedelta(seconds=duration_to_seconds(target) * len(days))

    def total_attendance(self, attandance_type: Attendance, date: str) -> int:
        """Count attendance of type up to date
        :param attandance_type: type to count
        :param date: up to this date
        :returns: count
        """
        days = [d for d in self.storage.get_dates() if d <= date]
        return sum(True for d in days if self.storage.get(d).attendance == attandance_type)

    def generate_report(self, is_local: bool = False) -> list[str]:  # pylint: disable=missing-param-doc,missing-return-doc
        """Generate report containing inconsistent days, missing attendance and other issues"""
        sorted_data = sorted(self.storage.get_dates())
        errors: list[str] = []
        for d in sorted_data:
            day = self.storage.get(d)
            if not day:
                raise ValueError(f"Missing day {d} is reported as present")
            try:
                day.check_consistency()
            except ValueError:
                errors.append(f"Inconsistent entries {d}")
            if day.attendance is None or day.attendance == Attendance.UNDEFINED and d <= datetime.date.today().isoformat():
                errors.append(f"Missing attendance {d}")
            if day.attendance == Attendance.VACATION and day.entries:
                errors.append(f"Vacation with time keeping entries {d}")
            if day.attendance == Attendance.SICK and day.entries:
                errors.append(f"Sick with time entries {d}")

            workdays = ["MON", "TUE", "WED", "THU", "FRI"]
        wdays: list[datetime.date] = get_workday_dates(workdays, sorted_data[0], sorted_data[-1])

        for wd in wdays:
            if wd.isoformat() not in self.storage.get_dates():
                errors.append(f"Missing workday {wd}")
        if is_local:
            print(errors)
        return errors

    def get_number_of_days(self) -> int:
        """Get number of days"""
        return len(self.storage.get_dates())

    def to_dict(self):
        """Export data as dict"""
        return {d: self.storage.get(d).to_dict() for d in self.storage.get_dates()}

    def from_dict(self, data):
        """Load data from dict"""
        for d in data:
            self.storage.update(Day.from_dict(data[d]))
