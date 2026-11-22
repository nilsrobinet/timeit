"""Migration helper for legacy json data"""

import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.time_keeper import Day


def main(file):
    print(file)
    with open(file) as f:
        import json

        data = json.load(f)

    new_data = {date: Day.from_dict(day, date) for date, day in data.items()}

    with open(file, "w") as f:
        import json

        json.dump({date: day.to_dict() for date, day in new_data.items()}, f, indent=4)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    main(args.file)
