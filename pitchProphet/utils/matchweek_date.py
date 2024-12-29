""""
Utility function that does the following based on data/match_dates/*.csv
    1. Find current matchweek for all league and return it
    2. Find if there are active matches
    3. Retrun a list of leagues with no active matches
"""

from pathlib import Path

import pandas as pd


def get_current_matchweek():
    f_path = Path(
        "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/match_dates/matchweek_dates_2024_2025.csv"
    )
    df = pd.read_csv(f_path)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])

    return


def main():
    get_current_matchweek()
    return


if __name__ == "__main__":
    main()
