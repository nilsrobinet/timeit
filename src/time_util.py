"""Utility functions for time calculations."""

from datetime import UTC, date, datetime

import cherrypy


def get_week_start(this_date: date | str) -> date:
    """Get start of week.
    :param this_date: Date in the target week.
    :returns: First day of the week.
    """
    if isinstance(this_date, str):
        this_date = datetime.fromisoformat(this_date).date()
    calendar_week = this_date.isocalendar()[1]
    return date.fromisocalendar(this_date.year, calendar_week, 1)


def duration_delta(worked: str, target: str) -> str:
    """Get difference between worked and target.
    All strings are in H:MM:SS format.
    :param worked: Worked time.
    :param target: Target time.
    :returns: Difference as a signed duration string.
    """
    worked_seconds = duration_to_seconds(worked)
    target_seconds = duration_to_seconds(target)
    diff = worked_seconds - target_seconds
    sign = "+" if diff >= 0 else "-"
    return f"{sign}{seconds_to_duration(abs(diff))}"


def duration_to_seconds(duration: str) -> int:
    """Convert duration to seconds.
    :param duration: Duration string.
    :returns: Duration in seconds.
    """
    text = str(duration).strip()
    day_count = 0
    time_part = text

    if "day" in text:
        day_text, time_part = text.split(",", 1)
        day_count = int(day_text.split()[0])
        time_part = time_part.strip()

    parts = time_part.split(":")
    if len(parts) != 3:
        raise cherrypy.HTTPError(400, f"Invalid duration format: {duration}")

    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(float(parts[2]))
    hours += day_count * 24
    return (hours * 3600) + (minutes * 60) + seconds


def seconds_to_duration(total_seconds: int) -> str:
    """Convert seconds to duration.
    :param total_seconds: Duration in seconds.
    :returns: Duration string in H:MM:SS format.
    """
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:01d}:{minutes:02d}:{seconds:02d}"


def parse_iso_datetime(s: str | None) -> datetime | None:
    """Parse ISO datetime string to datetime.
    :param s: ISO string.
    :returns: datetime or None.
    """
    if s is None:
        return None
    normalized = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as e:
        raise cherrypy.HTTPError(400, "timestamp must be ISO-8601") from e


def as_utc(t: datetime) -> datetime:
    """Convert to UTC.
    :param t: datetime
    :returns: UTC datetime
    """
    if t.tzinfo is None:
        return t.replace(tzinfo=UTC)
    return t.astimezone(UTC)
