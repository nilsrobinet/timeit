"""Migration helper for legacy json data"""

import os
import sys
import json
import datetime
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.time_keeper import Day, Attendance, Entry


def main(file):
    print(file)
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    new_data = {}
    for date, entries in data.items():
        day = Day(date, Attendance.UNDEFINED)
        for e in entries:
            entry = Entry.from_dict(e)
            day.add_entry(entry)
        new_data[date] = day

    with open(file, "w", encoding="utf-8") as f:
        json.dump({date: day.to_dict() for date, day in new_data.items()}, f, indent=4)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    main(args.file)
