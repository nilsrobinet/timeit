
from datetime import date, datetime


def get_week_start(this_date: date):
    if isinstance(this_date, str):
        this_date = datetime.fromisoformat(this_date).date()
    calendar_week = this_date.isocalendar()[1]
    return date.fromisocalendar(this_date.year, calendar_week, 1)