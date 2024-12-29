""""
Utility function that does the following based on data/match_dates/*.csv
    1. Find current matchweek for all league and return it
    2. Find if there are active matches
    3. Retrun a list of leagues with no active matches
"""

from pathlib import Path
from typing import Dict

import pandas as pd


def get_current_matchweek() -> Dict[str, bool]:
    """get current matchweek for all leageus from date"""
    f_path = Path(
        "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/match_dates/matchweek_dates_2024_2025.csv"
    )
    # load data
    df = pd.read_csv(f_path)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])

    # find current date
    today = pd.Timestamp.now()
    print(today)

    current_weeks = {}
    for league in df["league"].unique():
        league_df = df[df["league"] == league]

        # find the match week that contains today's date
        current_week = None
        for _, row in league_df.iterrows():
            if row["start_date"] <= today <= row["end_date"]:
                current_week = row["match_week"]
                break

        # if today is before the first match week
        if current_week is None and today < league_df["start_date"].min():
            current_week = league_df["match_week"].min()

        # if today is after the last match week
        elif current_week is None and today > league_df["end_date"].max():
            current_week = league_df["match_week"].max()

        # if today is between match weeks, return None for this league
        elif current_week is None:
            current_week = None

        current_weeks[league] = (
            current_week if current_week is None else int(current_week)
        )

    return current_weeks


def league_for_inference():
    "find which leage is eligible to generate inference-date for a given time"

    return


def main():
    print(get_current_matchweek())
    return


if __name__ == "__main__":
    main()
