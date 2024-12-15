import json
from typing import Dict, List

import pandas as pd
import yaml


def game_data_process(data: dict) -> pd.DataFrame:

    # Flatten dataset
    home_stat_df = pd.json_normalize(data, record_path="HomeStat").drop_duplicates()
    away_stat_df = pd.json_normalize(data, record_path="AwayStat").drop_duplicates()
    game_data_df = pd.json_normalize(data, record_path="MatchInfo").drop_duplicates()

    # Add first level index to make it multi-indexed
    home_stat_df.index = pd.MultiIndex.from_product([["HomeStat"], home_stat_df.index])
    away_stat_df.index = pd.MultiIndex.from_product([["AwayStat"], away_stat_df.index])
    game_data_df.index = pd.MultiIndex.from_product([["MatchInfo"], game_data_df.index])

    # Concatenate data along the index to maintain separation of data
    combined_df = pd.concat([game_data_df, home_stat_df, away_stat_df], axis=0)

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
        # finding last n occurance of matches for home and away team in a given row from MatchInfo
        away_team = self.data[
            (self.data["HomeTeam"] == row["AwayTeam"])
            | (self.data["AwayTeam"] == row["AwayTeam"])
        ].iloc[1 : self.n]
        home_team = self.data[
            (self.data["HomeTeam"] == row["HomeTeam"])
            | (self.data["AwayTeam"] == row["HomeTeam"])
        ].iloc[1 : self.n]

        # finding position index from inner index , to filter value using outer index -> HomeStat and AwayStat
        position_index_home = home_team.index.get_loc("MatchInfo")
        position_index_away = away_team.index.get_loc("MatchInfo")

        # use the slice object with integer position to find last n team stats
        return


def main():
    json_path = (
        "/Users/paraspokharel/Programming/costomFPL/costomFPL/data/fbref/trial90.json"
    )

    # convert json to python dict
    data = open_json(json_path)

    # convert json game data into multi-index dataframe
    data = game_data_process(data)

    # process statistics
    stats = DataFrameStats(data, 5)
    table = stats.get_last_n_data(data.iloc[0])
    print(table)


if __name__ == "__main__":
    main()
