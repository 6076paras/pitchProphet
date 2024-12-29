from pathlib import Path

import pandas as pd

from pitchProphet.utils.matchweek_date import get_dates_for_gameweek


def find_league_predictions() -> dict:
    """find the latest prediction files for each league and their match weeks and dates"""
    tables_dir = Path(
        "/Users/paraspokharel/Programming/pitchProphet/web/static/assets/tables"
    )
    leagues = ["Bundesliga", "La-Liga", "Premier-League", "Serie-A"]
    league_files = {}

    for league in leagues:

        pattern = f"{league}_week_*_predictions.csv"
        matching_files = list(tables_dir.glob(pattern))

        if matching_files:
            latest_file = None
            latest_week = -1

            for file in matching_files:
                try:
                    week_str = file.stem.split("week_")[1].split("_")[0]
                    week_num = int(week_str)
                    if week_num > latest_week:
                        latest_week = week_num
                        latest_file = file
                except (IndexError, ValueError):
                    continue

            if latest_file:
                league_files[league] = {"file": latest_file, "match_week": latest_week}

    return league_files


def get_predictions() -> dict:
    """load match predictions for all leagues from CSV files."""

    league_files = find_league_predictions()
    league_data = {}

    for league, info in league_files.items():
        try:
            df = pd.read_csv(info["file"])

            # round probabilities to 3 decimal places
            prob_columns = [col for col in df.columns if col.startswith("p(")]
            df[prob_columns] = df[prob_columns].round(3)

            # convert DataFrame to HTML table
            html_table = df.to_html(
                classes="table table-striped shadow table-hover", index=False
            )

            league_data[league] = {
                "table": html_table,
                "match_week": info["match_week"],
            }
        except Exception as e:
            print(f"Error loading predictions for {league}: {e}")
            continue

    return league_data
