import json

import pandas as pd
import yaml


def flattan_json(path: str) -> pd.DataFrame:
    """
    Loads json file into pd.Dataframe
    return pd.read_csv(path)
    by flattening.
    """
    pass


def calc_stats(n, data):
    """
    Dataframe map that generates statistics, f(data_i) using last its last n
    values
    """
    # standard deviation

    # mean

    # slope

    pass


def extract_relv(data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract relevent data
    """
    pass


def main():
    json_path = "/Users/paraspokharel/Programming/costomFPL/costomFPL/data/fbref/2023-2024-Premier-League-3-matches.json"
    with open(json_path, "r") as file:
        data = json.load(file)
    normalized = pd.json_normalize(data)
    print(normalized.columns)
    # Normalize the data

    # Flatten HomeStat
    home_stat_df = pd.json_normalize(data, record_path="HomeStat")
    away_stat_df = pd.json_normalize(data, record_path="AwayStat")
    game_data_df = pd.json_normalize(data, record_path="MatchInfo")

    # Add the level for first index based on the section name
    home_stat_df.index = pd.MultiIndex.from_product([["HomeStat"], home_stat_df.index])
    away_stat_df.index = pd.MultiIndex.from_product([["AwayStat"], away_stat_df.index])
    game_data_df.index = pd.MultiIndex.from_product([["MatchInfo"], game_data_df.index])

    # Now, concatenate all DataFrames into one with MultiIndex
    final_df = pd.concat([game_data_df, home_stat_df, away_stat_df])
    print(final_df)


if __name__ == "__main__":
    main()
