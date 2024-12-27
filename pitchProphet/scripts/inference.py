import glob
import sys
from typing import List

import pandas as pd
import yaml

from pitchProphet.data.fbref.fbref_scrapper import FBRefScraper
from pitchProphet.data.pre_processing.calculate_stats import DescriptiveStats
from pitchProphet.data.pre_processing.load_data import LoadData


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
    """scrapp last 60 matches from fbref"""
    # TODO: scrapp for each league
    scraper = FBRefScraper(config_path)
    scraper.scrape_season("2024-2025", league, inference=True)
    return


def load_data(inference_raw_pth, config_path):
    """convert json game data into multi-indexed dataframe"""
    # TODO: load data sepeately for each league
    ld_data = LoadData(inference_raw_pth, config_path)
    data = ld_data.game_data_process()
    return data


def add_stats(fixtures, data, n=5):
    """add historical stats for each team in the fixtures."""
    # Initialize DescriptiveStats with inference mode
    stats_calculator = DescriptiveStats(data, n=n, inference=True)

    all_home_stats = []
    all_away_stats = []

    # Process each fixture
    for _, row in fixtures.iterrows():
        try:
            # Calculate stats for the match
            match_stats = stats_calculator.process_home_away_features(row)
            all_home_stats.append(match_stats["home_stats"])
            all_away_stats.append(match_stats["away_stats"])
        except Exception as e:
            print(f"Error processing fixture: {e}")
            continue

    # Convert lists to DataFrames
    home_stats_df = pd.DataFrame(all_home_stats)
    away_stats_df = pd.DataFrame(all_away_stats)

    return {"home_data": home_stats_df, "away_data": away_stats_df}


def process_data(data):
    # process data for inference
    home_stat = data["home_data"]
    away_stat = data["away_data"]
    if "Unnamed: 0" in home_stat.columns:
        home_stat.drop(columns=["Unnamed: 0"], inplace=True)
    if "Unnamed: 0" in away_stat.columns:
        away_stat.drop(columns=["Unnamed: 0"], inplace=True)

    # rename columns
    home_stat.columns = ["h" + col for col in home_stat.columns]
    away_stat.columns = ["a" + col for col in away_stat.columns]
    x_df = pd.concat([home_stat, away_stat], axis=1)
    x_df = x_df.apply(pd.to_numeric)
    return x_df


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

    # TODO: scrapp data depending upon a condition
    # data = inference_raw_data(config_path, league)

    # TODO: pre-process specific data and depending upoing condition
    # pre-process inference data
    data = load_data(inference_raw_pth, config_path)
    inf_input = add_stats(fixtures, data)
    print(inf_input)

    # predicttion
    processed_data = process_data(inf_input)


# predictions = return_predict(inf_input)


if __name__ == "__main__":
    main()
