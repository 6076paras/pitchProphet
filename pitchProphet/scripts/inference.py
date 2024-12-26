import glob
import sys
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


def load_data(inference_raw_pth, config_path):
    # convert json game data into multi-indexed dataframe
    ld_data = LoadData(inference_raw_pth, config_path)
    data = ld_data.game_data_process()
    return data


def add_stats(fixtures, data, n=5):

    # loop throguh each fixtrue
    for index, row in fixtures.iterrows():

        # TODO: add in calculate_stats.py using inference == True and this is repeted!!
        # get group of matches for each fixture
        match_info = data.loc["MatchInfo"]
        home_team = row["Home"]
        away_team = row["Away"]
        home_indices = match_info[
            (
                (match_info["HomeTeam"] == home_team)
                | (match_info["AwayTeam"] == home_team)
            )
        ].index[:n]
        away_indices = match_info[
            (
                (match_info["HomeTeam"] == home_team)
                | (match_info["AwayTeam"] == home_team)
            )
        ].index[:n]

        # get stats for home team's matches from idx of last n home matches
        home_data = pd.DataFrame()
        for idx in home_indices:
            match_slice = data.xs(idx, level=1)
            if match_info.loc[idx, "HomeTeam"] == home_team:
                stats = match_slice.loc["HomeStat"]
            else:
                stats = match_slice.loc["AwayStat"]
            home_data = pd.concat([home_data, stats.to_frame().T])

        # get stats for away team's matches from the ixs of last n away matches
        away_data = pd.DataFrame()
        for idx in away_indices:
            match_slice = data.xs(idx, level=1)
            if match_info.loc[idx, "HomeTeam"] == away_team:
                stats = match_slice.loc["HomeStat"]
            else:
                stats = match_slice.loc["AwayStat"]
            away_data = pd.concat([away_data, stats.to_frame().T])

        # drop NA columns
        home_data = home_data.dropna(axis=1)
        away_data = away_data.dropna(axis=1)

        return {"home_data": home_data, "away_data": away_data}


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
    inference_raw_pth = "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/fbref/raw/inference"

    # data = inference_raw_data(config_path, league)

    # pre-process inference data
    data = load_data(inference_raw_pth, config_path)
    print(data)
    print(add_stats(fixtures, data))


if __name__ == "__main__":
    main()
