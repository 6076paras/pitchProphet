import glob
import json
from pathlib import Path
from typing import List

import pandas as pd
import yaml


class LoadData:
    """
    Class for loading and match data from raw data scrapped from
    fbref.com to pandas dataframe.

    Attributes:
        raw_dir (str): Path to the JSON file with match data.
        config_path (str): Path to the YAML configuration file.
    Methods:
        game_data_process() -> pd.DataFrame:
            Processes and returns a DataFrame of all match data.
    """

    def __init__(
        self,
        config_path: str,
        league: str = None,
        match_week: int = None,
        player_data: bool = False,
        inference: bool = False,
    ):
        self.config_path = config_path
        self.league = league
        self.match_week = match_week
        self.player_data = player_data
        self.inference = inference
        self.all_config = self._open_yaml(self.config_path)
        self.config = self.all_config["processing"]
        self.paths = self.all_config["global"]["paths"]
        self.raw_dir = (
            Path(self.paths["root_dir"]) / Path(self.paths["raw_dir"]) / "team_data"
        )
        if self.player_data == True:
            self.raw_dir = (
                Path(self.paths["root_dir"])
                / Path(self.paths["raw_dir"])
                / "team_and_player_data"
            )
        if self.inference == True:
            self.raw_dir = (
                Path(self.paths["root_dir"]) / Path(self.paths["raw_dir"]) / "inference"
            )

        self.data = self._open_json(self._find_relv_files())

    def game_data_process(self) -> pd.DataFrame:
        """
        Processes match data by flattening the dataset and filtering variables.

        Returns:
            pd.DataFrame: A multi-indexed DataFrame, concatenated from:
            1. General game info
            2. Home team statistics
            3. Away team statistics
        """

        # TODO: drop duplicate hinders synthetic copies of data
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

        return pd.concat([game_data_df, home_stat_df, away_stat_df], axis=0)

    def _filter_x_vars(
        self, home_player_df: pd.DataFrame, away_player_df: pd.DataFrame, x_vars: list
    ):
        """only include variables listed in config"""
        return home_player_df[x_vars], away_player_df[x_vars]

    def _find_relv_files(self):
        """iterate through raw file dir and return relevant files based on filters"""
        pattern = f"{self.raw_dir}/*.json"
        str_match_week = str(self.match_week) if self.match_week is not None else None

        # get all JSON files and retrun if no filters
        all_files = glob.glob(pattern)
        if not self.league and not str_match_week:
            return all_files

        # ilter files based on league and match week if specified
        filtered_files = []
        for file in all_files:
            # check league filter if specified
            if self.league and self.league not in file:
                continue
            # check match week filter if specified
            if str_match_week and f"match_week-{str_match_week}" not in file:
                continue
            filtered_files.append(file)
        if not self.league and not str_match_week:
            return all_files

        if not filtered_files:
            print(
                f"Warning: No files found matching league='{self.league}' and match_week='{self.match_week}'"
            )
            return []
        print(filtered_files)

        return filtered_files

    def _open_json(self, all_json: List[str]) -> dict:
        combined_data = []
        for file in all_json:
            with open(file, "r") as file:
                data = json.load(file)
                combined_data.extend(data)
        return combined_data

    def _open_yaml(self, config_path: str) -> dict:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        return config
