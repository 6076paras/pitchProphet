from typing import List

import pandas as pd
import yaml

from pitchProphet.data.fbref.fbref_scrapper import FBRefScraper
from pitchProphet.data.pre_processing.load_data import LoadData
from pitchProphet.data.pre_processing.process import Process


def get_fixtures(match_week: int, url: str) -> pd.DataFrame:
    """returns a fixture list from FBRef for a given match week."""
    try:
        all_fixtures = pd.read_html(url)
        week_fixtures = all_fixtures[0][all_fixtures[0]["Wk"] == match_week]
        team_list = week_fixtures[["Home", "Away"]].reset_index(drop=True)
        team_list.name = f"Matchweek {match_week}"
        return team_list
    except Exception as e:
        print(f"Error fetching fixtures: {e}")
        return pd.DataFrame()


def load_config(path: str) -> dict:
    """loads the configuration from a YAML file."""
    try:
        with open(path, "r") as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}


def inference_raw_data(config_path, league):
    # scrapp
    scraper = FBRefScraper(config_path)
    scraper.scrape_season("2024-2025", league, inference=True)
    return


def main():
    config_path = (
        "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/config/config.yaml"
    )
    config = load_config(config_path)

    # get fixtures
    try:
        league = "Premier-League"
        league_id = config["scraper"]["league_ids"][league]
        url = f"{config['scraper']['base_url']}/{league_id}/2024-2025/schedule/2024-2025-{league}-Scores-and-Fixtures"
        match_week = 10
        fixtures = get_fixtures(match_week, url)
        if not fixtures.empty:
            print(fixtures)
        else:
            print("No fixtures found.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # get raw inference data
    data = inference_raw_data(config_path, league)

    # process inference data


if __name__ == "__main__":
    main()
