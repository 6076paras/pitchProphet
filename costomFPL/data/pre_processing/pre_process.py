import json
from typing import Dict, List

import pandas as pd
import yaml


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


def open_json(json_path: str) -> dict:
    with open(json_path, "r") as file:
        data = json.load(file)
    return data


class DataFrameStats:
    """
    Class: DataFrameStat
    Description: This class provides methods for calculating various statistics for the data.
    """

    def __init__(self, data: pd.DataFrame, n: int):
        self.data = data
        self.n = n

    # last numbers for last n matches for home team and away team
    def get_last_n_data(self, row: pd.Series) -> List[pd.DataFrame]:
        """
        Returns list of pandas dataframe for all the game related statistics
        of last n home and away matches
        """
        # filter data frame by home and away team for previous 5 games
        home_last5 = (
            self.data[self.data["HomeTeam"] == row["HomeTeam"]]
            .head(self.n + 1)
            .tail(self.n)
        )
        away_last5 = (
            self.data[self.data["AwayTeam"] == row["AwayTeam"]]
            .head(self.n + 1)
            .tail(self.n)
        )

        return [home_last5, away_last5]


def main():
    json_path = "/Users/paraspokharel/Programming/costomFPL/costomFPL/data/fbref/2023-2024-Premier-League-20-matches.json"

    # convert json to python dict
    data = open_json(json_path)

    # convert json game data into multi-index dataframe
    data = game_data_process(data)
    print(data)
    # process statistics
    stats = DataFrameStats(data, 5)
    table = stats.get_last_n_data(data.iloc[0])
    print(table)


if __name__ == "__main__":
    main()
