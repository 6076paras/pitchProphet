import glob
import pickle
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
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


def check_existing_data(inference_raw_pth: str, league: str, match_week: int) -> bool:
    """check if data for the specified league and match week exists"""
    match_week = str(match_week)
    pattern = f"{inference_raw_pth}/*{league}*match_week-{match_week}*.json"
    existing_files = glob.glob(pattern)
    print(existing_files)
    return len(existing_files) > 0


def inference_raw_data(
    config_path: str, league: str, match_week: int, force_scrape: bool = False
) -> None:
    """scrape last 80 matches from fbref if data doesn't exist"""

    inference_raw_pth = "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/fbref/raw/inference"

    # check if we need to scrape
    if not force_scrape and check_existing_data(
        inference_raw_pth, league, match_week=None
    ):
        print(f"\nFound existing data for {league} week {match_week}")
        return

    print(f"\nScraping data for {league} week {match_week}...")
    scraper = FBRefScraper(config_path, inference=True)
    scraper.scrape_season("2024-2025", league)
    return


def load_data(inference_raw_pth, config_path, league=None, match_week=None):
    """convert json game data into multi-indexed dataframe"""
    # load data with optional league and match week filters
    ld_data = LoadData(
        inference_raw_pth, config_path, league=league, match_week=match_week
    )
    data = ld_data.game_data_process()
    return data


def add_stats(fixtures, data, n=5):
    """add historical stats for each team in the fixtures."""
    # initialize DescriptiveStats with inference mode
    stats_calculator = DescriptiveStats(data, n=n, inference=True)

    all_home_stats = []
    all_away_stats = []

    # process each fixture
    for _, row in fixtures.iterrows():
        try:
            # Calculate stats for the match
            match_stats = stats_calculator.process_home_away_features(row)
            all_home_stats.append(match_stats["home_stats"])
            all_away_stats.append(match_stats["away_stats"])
        except Exception as e:
            print(f"Error processing fixture: {e}")
            continue

    # convert lists to DataFrames
    home_stats_df = pd.DataFrame(all_home_stats)
    away_stats_df = pd.DataFrame(all_away_stats)

    return {"home_data": home_stats_df, "away_data": away_stats_df}


def process_data(data: Dict[str, pd.DataFrame], model_path: str) -> pd.DataFrame:
    """process data and make predictions using the loaded model"""

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

    # combine features
    x_df = pd.concat([home_stat, away_stat], axis=1)
    x_df = x_df.apply(pd.to_numeric)

    # load model
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    # make predictions
    # predictions = model.predict(x_df)
    probabilities = model.predict_proba(x_df)

    # create results DataFrame
    results = pd.DataFrame(
        {
            "p(Home Win)": probabilities[:, 0],
            "p(Draw)": probabilities[:, 1],
            "p(Away Win)": probabilities[:, 2],
        }
    )
    return results


def save_predictions(results: pd.DataFrame, league: str, match_week: int) -> None:
    """save prediction results to CSV file in web assets directory"""
    # TODO: think about refactoring later!
    # create directory path
    save_dir = Path(
        "/Users/paraspokharel/Programming/pitchProphet/web/static/assets/tables"
    )
    save_dir.mkdir(parents=True, exist_ok=True)

    # create filename with league and match week
    filename = f"{league}_week_{match_week}_predictions.csv"
    save_path = save_dir / filename

    # save to CSV
    results.to_csv(save_path, index=False)
    print(f"\nPredictions saved to: {save_path}")
    return


def main():
    config_path = (
        "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/config/config.yaml"
    )
    model_path = "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/models/xgb_model.pkl"
    config = load_config(config_path)

    # get fixtures
    try:
        league = "Bundesliga"
        league_id = config["scraper"]["league_ids"][league]
        url = f"{config['scraper']['base_url']}/{league_id}/2024-2025/schedule/2024-2025-{league}-Scores-and-Fixtures"
        match_week = 16
        fixtures = get_fixtures(match_week, url)
        if not fixtures.empty:
            print("\nFixtures:")
            print(fixtures)
        else:
            print("No fixtures found.")
            return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

    inference_raw_pth = "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/fbref/raw/inference"

    # only scrape if data doesn't exist
    data = inference_raw_data(config_path, league, match_week=None)

    # pre-process inference data with league and match week filters
    data = load_data(
        inference_raw_pth, config_path, league=league, match_week=match_week
    )
    inf_input = add_stats(fixtures, data)

    # get predictions
    predictions = process_data(inf_input, model_path)

    # combine fixtures with predictions
    results = pd.concat([fixtures, predictions], axis=1)
    print("\nPredictions:")
    print(results)

    # save predictions to CSV
    save_predictions(results, league, match_week)


if __name__ == "__main__":
    main()
