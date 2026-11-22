"""Tests for time keeper model serialization."""

import datetime
import json
from types import SimpleNamespace

from main import TimeIt
from src.time_keeper import Attendance, Day, Entry, EntryType, TimeKeeper


def test_day_dict_round_trip():
    timestamp = datetime.datetime(2026, 11, 22, 10, 30, tzinfo=datetime.UTC)
    day = Day("2026-11-22", Attendance.REMOTE)
    day.add_entry(Entry(EntryType.START, timestamp, 12))

    serialized = day.to_dict()
    restored = Day.from_dict(serialized)

    assert serialized["entries"][0]["timestamp"] == timestamp.isoformat()
    assert restored.date == day.date
    assert restored.attendance is day.attendance
    assert restored.entries[0].type is EntryType.START
    assert restored.entries[0].timestamp == timestamp
    assert restored.entries[0].id == 12


def test_day_from_legacy_dict_uses_key_as_date_and_default_attendance():
    day = Day.from_dict(
        {
            "attendance": "undefined",
            "entries": [{"type": "start", "timestamp": "2026-11-22T10:30:00", "id": 1}],
        },
        "2026-11-22",
    )

    assert day.date == "2026-11-22"
    assert day.attendance is Attendance.UNDEFINED
    assert day.entries[0].timestamp == datetime.datetime(2026, 11, 22, 10, 30, tzinfo=datetime.UTC)


def test_time_keeper_loads_and_saves_json(tmp_path):
    data_path = tmp_path / "data.json"
    data_path.write_text(
        json.dumps(
            {
                "2026-11-22": {
                    "attendance": "sick",
                    "entries": [
                        {
                            "type": "stop",
                            "timestamp": "2026-11-22T10:30:00+00:00",
                            "id": 5,
                        }
                    ],
                }
            }
        ),
        encoding="utf-8",
    )

    time_keeper = TimeKeeper(data_path)
    time_keeper.load_data()

    assert time_keeper.data["2026-11-22"].attendance is Attendance.SICK
    assert time_keeper.current_entry_id == 6

    time_keeper.save_data()
    reloaded = TimeKeeper(data_path)
    reloaded.load_data()

    assert reloaded.data["2026-11-22"].entries[0].type is EntryType.STOP
    assert reloaded.data["2026-11-22"].entries[0].timestamp == datetime.datetime(2026, 11, 22, 10, 30, tzinfo=datetime.UTC)


def test_summary_serializes_last_entry():
    date = "2026-11-22"
    day = Day(date, Attendance.UNDEFINED)
    day.add_entry(Entry(EntryType.START, datetime.datetime(2026, 11, 22, 9, tzinfo=datetime.UTC), 1))
    day.add_entry(Entry(EntryType.STOP, datetime.datetime(2026, 11, 22, 10, tzinfo=datetime.UTC), 2))
    time_keeper = TimeKeeper()
    time_keeper.data[date] = day

    app = TimeIt.__new__(TimeIt)
    app.config = SimpleNamespace(get_daily_target=lambda: "0:00:00")
    app.time_keeper = time_keeper

    response = app._summary_get({"date": date})
    decoded = json.loads(json.dumps(response))

    assert decoded["last_entry"] == day.entries[-1].to_dict()
