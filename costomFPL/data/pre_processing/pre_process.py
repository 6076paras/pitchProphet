import json

import pandas as pd
import yaml


def calc_stats(n, data):
    """
    Dataframe map that generates statistics, f(data_i) using last its last n
    values
    """
    # standard deviation

    # mean

    # slope

    pass


def game_data_process(data: dict) -> pd.DataFrame:

    # flatten dataset
    home_stat_df = pd.json_normalize(data, record_path="HomeStat")
    away_stat_df = pd.json_normalize(data, record_path="AwayStat")
    game_data_df = pd.json_normalize(data, record_path="MatchInfo")

    # add first level index to make it multi index obj
    home_stat_df.index = pd.MultiIndex.from_product([["HomeStat"], home_stat_df.index])
    away_stat_df.index = pd.MultiIndex.from_product([["AwayStat"], away_stat_df.index])
    game_data_df.index = pd.MultiIndex.from_product([["MatchInfo"], game_data_df.index])

    return pd.concat([game_data_df, home_stat_df, away_stat_df])


def open_json(file_path: str) -> dict:
    with open(json_path, "r") as file:
        data = json.load(file)
    return data


def main():
    json_path = "/Users/paraspokharel/Programming/costomFPL/costomFPL/data/fbref/2023-2024-Premier-League-3-matches.json"

    # convert json to python dict
    data = open_json(json_path)

    # convert json game data into multi-index dataframe
    data = game_data_process(data)

    #


if __name__ == "__main__":
    main()
