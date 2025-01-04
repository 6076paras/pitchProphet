""""
Utility functions based on data/match_dates/*.csv
    1. Find current matchweek for all league and return it
    2. Find if there are active matches
    3. Retrun a list of leagues with no active matches
"""

from pathlib import Path
from typing import Dict, List

import pandas as pd


def get_current_matchweek() -> Dict[str, bool]:
    """get current matchweek for all leagues from match_dates/*.csv"""
    main_dir = Path(__file__).resolve().parent.parent
    f_path = main_dir / Path("data/match_dates/matchweek_dates_2024_2025.csv")

    # load data
    df = pd.read_csv(f_path)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])

    # find current date
    today = pd.Timestamp.now()

    leagues = ["Bundesliga", "La-Liga", "Premier-League", "Serie-A"]
    current_weeks = {}

    for league in leagues:
        league_df = df[df["league"] == league]
        if league_df.empty:
            print(f"Warning: No data found for {league}")
            current_weeks[league] = None
            continue

        # find the match week that contains today's date
        current_week = None
        for _, row in league_df.iterrows():
            if row["start_date"] <= today <= row["end_date"]:
                # active matches, return None
                current_weeks[league] = None
                break
        else:
            # no active matches, find the previous match week
            past_weeks = league_df[league_df["end_date"] < today]
            if not past_weeks.empty:
                current_weeks[league] = int(past_weeks.iloc[-1]["match_week"])
            else:
                current_weeks[league] = None

    return current_weeks


def get_leagues_for_inference() -> Dict[str, bool]:
    """get which leagues need inference data based on active matches"""
    current_weeks = get_current_matchweek()
    # for each league, True if no active matches (week is None)
    leagues = ["Bundesliga", "La-Liga", "Premier-League", "Serie-A"]
    return {league: current_weeks.get(league) is None for league in leagues}


def get_dates_for_gameweek(match_week: int) -> Dict[str, List]:
    "get start date and end date for a given matchweek and league"
    # TODO: refactor/cleanup
    f_path = Path(
        "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/match_dates/matchweek_dates_2024_2025.csv"
    )
    # load data
    df = pd.read_csv(f_path)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])

    # loop throguh
    dates = {}
    leagues = ["Bundesliga", "La-Liga", "Premier-League", "Serie-A"]
    for league in leagues:
        match_df = df[(df["league"] == league) & (df["match_week"] == match_week)]
        dates[league] = {
            "start_date": match_df["start_date"].dt.strftime("%Y-%m-%d").values[0],
            "end_date": match_df["end_date"].dt.strftime("%Y-%m-%d").values[0],
        }
    return dates


"""
def main():
    match_week = 1
    result = get_dates_for_gameweek(match_week)
    print(result)
    return


if __name__ == "__main__":
    main()
"""
