import glob
import pickle
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yaml

from pitchProphet.data.fbref.fbref_scrapper import FBRefScraper
from pitchProphet.data.pre_processing.calculate_stats import DescriptiveStats
from pitchProphet.data.pre_processing.load_data import LoadData
from pitchProphet.utils.matchweek_date import get_current_matchweek


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


def check_existing_data(inference_raw_pth: Path, league: str, match_week: int) -> bool:
    """check if data for the specified league and match week exists"""
    match_week = str(match_week)
    pattern = f"{str(inference_raw_pth)}/*{league}*match_week-{match_week}*.json"
    existing_files = glob.glob(pattern)
    if existing_files:
        print(f"\nFound existing data file(s):")
        for f in existing_files:
            print(f"- {Path(f).name}")
        return True
    return False


def inference_raw_data(
    config: dict,
    config_path: Path,
    league: str,
    match_week: int,
    force_scrape: bool = False,
) -> bool:
    """scrape match data if it doesn't exist or if force_scrape is True"""
    inference_raw_pth = Path(config["global"]["paths"]["inference_dir"])
    # if data exists and we're not forcing a scrape, use existing data
    if not force_scrape and check_existing_data(inference_raw_pth, league, match_week):
        print(f"Using existing data for {league} week {match_week}")
        return True

    # data doesn't exist or force_scrape=True, so scrape new data
    print(f"\nScraping data for {league} week {match_week}...")
    try:
        scraper = FBRefScraper(config_path, inference=True)
        scraper.scrape_season("2024-2025", league)
        return True
    except Exception as e:
        print(f"Error scraping data: {e}")
        return False


def load_data(inference_raw_pth, config_path, league=None, match_week=None):
    """convert json game data into multi-indexed dataframe"""
    # load data with optional league and match week filters
    inference_raw_pth = str(inference_raw_pth)
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


def process_data(data: Dict[str, pd.DataFrame], model_path: Path) -> pd.DataFrame:
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


def save_predictions(
    config: dict, results: pd.DataFrame, league: str, match_week: int
) -> None:
    """save prediction results to CSV file in web assets directory"""
    # TODO: think about refactoring later!
    # create directory path
    save_dir = Path(config["global"]["root_dir"]) / config["inference"]["output_dir"]
    save_dir.mkdir(parents=True, exist_ok=True)

    # create filename with league and match week
    filename = f"{league}_week_{match_week}_predictions.csv"
    save_path = save_dir / filename

    # save to CSV
    results.to_csv(save_path, index=False)
    print(f"\nPredictions saved to: {save_path}")
    return


def main():
    script_dir = Path(__file__).parent.parent
    config_path = script_dir / "config" / "config.yaml"
    config = load_config(config_path)

    # get current match weeks for all leagues
    current_weeks = get_current_matchweek()

    # process each league
    for league, current_week in current_weeks.items():
        try:
            # skip if there are active matches (current_week is None)
            if current_week is None:
                print(f"\nSkipping {league} - active matches or no data")
                continue

            print(f"\nProcessing {league}...")
            league_id = config["scraper"]["league_ids"][league]
            url = f"{config['scraper']['base_url']}/{league_id}/2024-2025/schedule/2024-2025-{league}-Scores-and-Fixtures"

            next_week = current_week + 1
            print(f"Getting fixtures for week {next_week}")

            # get fixtures for next week
            fixtures = get_fixtures(next_week, url)
            if fixtures.empty:
                print(f"No fixtures found for {league} week {next_week}")
                continue

            print(f"\nFixtures for {league} week {next_week}:")
            print(fixtures)

            # check for existing data, don't force scrape
            if not inference_raw_data(
                config,
                config_path,
                league,
                match_week=next_week - 1,
                force_scrape=False,
            ):
                print(f"Skipping {league} - no data available for week {next_week - 1}")
                continue

            # pre-process inference raw data
            inference_raw_pth = Path(config["global"]["paths"]["inference_dir"])
            data = load_data(
                inference_raw_pth, config_path, league=league, match_week=current_week
            )
            if data.empty:
                print(f"No data available for {league} week {next_week}")
                continue

            inf_input = add_stats(fixtures, data)

            model_path = Path(config["global"]["paths"]["model_dir"]) / "xgb_model.pkl"
            predictions = process_data(inf_input, model_path)

            # combine fixtures with predictions
            results = pd.concat([fixtures, predictions], axis=1)
            print(f"\nPredictions for {league}:")
            print(results)

            # save

            save_predictions(config, results, league, next_week)

        except Exception as e:
            print(f"Error processing {league}: {e}")
            continue


if __name__ == "__main__":
    main()
