import json

import pandas as pd
import yaml


class LoadData:
    """
    Class for loading and match data from raw data scrapped from
    fbref.com to pandas dataframe.

    Attributes:
        json_path (str): Path to the JSON file with match data.
        config_path (str): Path to the YAML configuration file.
    Methods:
        game_data_process() -> pd.DataFrame:
            Processes and returns a DataFrame of all match data.
    """

    def __init__(self, json_path: str, config_path: str):
        self.json_path = json_path
        self.config_path = config_path
        self.data = self._open_json(self.json_path)
        self.config = self._open_yaml(self.config_path)["processing"]

    def game_data_process(self) -> pd.DataFrame:
        """
        Processes match data by flattening the dataset and filtering variables.

        Returns:
            pd.DataFrame: A multi-indexed DataFrame, concatenated from:
            1. General game info
            2. Home team statistics
            3. Away team statistics
        """

        # flatten dataset
        home_stat_df = pd.json_normalize(
            self.data, record_path="HomeStat"
        ).drop_duplicates()
        away_stat_df = pd.json_normalize(
            self.data, record_path="AwayStat"
        ).drop_duplicates()
        game_data_df = pd.json_normalize(
            self.data, record_path="MatchInfo"
        ).drop_duplicates()

        # filter out variables as defined in config file
        home_stat_df, away_stat_df = self._filter_x_vars(
            home_stat_df, away_stat_df, self.config["x_vars"]
        )

        # add first level index to make it multi-indexed
        home_stat_df.index = pd.MultiIndex.from_product(
            [["HomeStat"], home_stat_df.index]
        )
        away_stat_df.index = pd.MultiIndex.from_product(
            [["AwayStat"], away_stat_df.index]
        )
        game_data_df.index = pd.MultiIndex.from_product(
            [["MatchInfo"], game_data_df.index]
        )
        game_data = pd.concat([game_data_df, home_stat_df, away_stat_df], axis=0)

        # retrun the order of rows, as the last game should be first in the table
        return game_data.iloc[::-1]

    def _filter_x_vars(
        self, home_player_df: pd.DataFrame, away_player_df: pd.DataFrame, x_vars: list
    ):
        """only include variables listed in config"""
        return home_player_df[x_vars], away_player_df[x_vars]

    def _open_json(self, json_path: str) -> dict:
        with open(json_path, "r") as file:
            data = json.load(file)
        return data

    def _open_yaml(self, config_path: str) -> dict:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        return config
