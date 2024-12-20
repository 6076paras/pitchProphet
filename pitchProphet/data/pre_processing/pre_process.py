"""
Pre-processing module for soccer match data.

This module handles loading and processing of soccer match statistics from JSON files.
The core implementation strategy uses separate index-based manipulation of three main
data components (match info, home stats, away stats) rather than hierarchical access
(manipulating multi-indexed object at once).

Key components:
- LoadData: Handles JSON data loading and DataFrame creation
- DataFrameStats: Processes data for statistics such as mean, varience..for reach 
    home and away teams's last n matches. 

"""

import json
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import yaml


class LoadData:

    def __init__(self, json_path: str, config_path: str):
        self.json_path = json_path
        self.config_path = config_path
        self.data = self._open_json(self.json_path)
        self.config = self._open_yaml(self.config_path)["processing"]

    def game_data_process(self) -> pd.DataFrame:

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

    def _open_json(self, json_path: str) -> dict:
        with open(json_path, "r") as file:
            data = json.load(file)
        return data

    def _open_yaml(self, config_path: str) -> dict:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        return config


class DataFrameStats:
    """
    Class: DataFrameStat
    Description: This class provides methods for calculating various statistics for the data.
    """

    def __init__(self, data: pd.DataFrame, n=5):
        self.data = data
        self.n = n

    def get_last_n_data(self, row: pd.Series) -> Dict[str, pd.DataFrame]:
        """
        Returns list of pandas dataframe for all the game related statistics
        of last n home and away matches
        """
        # get team names from the match info
        home_team = row["HomeTeam"]
        away_team = row["AwayTeam"]
        current_idx = row.name

        print(f"\nProcessing match: Home={home_team} vs Away={away_team}")
        print(f"Current index: {current_idx}")

        # get all match indices where teams played
        match_info = self.data.loc["MatchInfo"]

        # debug print
        # print("\nMatch info shape:", match_info.shape)
        # print("Available teams:", match_info["HomeTeam"].unique())

        away_indices = match_info[
            (
                (match_info["HomeTeam"] == away_team)
                | (match_info["AwayTeam"] == away_team)
            )
            & (match_info.index != current_idx)
        ].index[: self.n]

        home_indices = match_info[
            (
                (match_info["HomeTeam"] == home_team)
                | (match_info["AwayTeam"] == home_team)
            )
            & (match_info.index != current_idx)
        ].index[: self.n]

        # print(f"\nFound indices - Home: {home_indices}, Away: {away_indices}")

        # get stats for home team's matches from idx of last n home matches
        home_data = pd.DataFrame()
        for idx in home_indices:
            match_slice = self.data.xs(idx, level=1)
            if match_info.loc[idx, "HomeTeam"] == home_team:
                stats = match_slice.loc["HomeStat"]
            else:
                stats = match_slice.loc["AwayStat"]
            home_data = pd.concat([home_data, stats.to_frame().T])

        # get stats for away team's matches from the ixs of last n away matches
        away_data = pd.DataFrame()
        for idx in away_indices:
            match_slice = self.data.xs(idx, level=1)
            if match_info.loc[idx, "HomeTeam"] == away_team:
                stats = match_slice.loc["HomeStat"]
            else:
                stats = match_slice.loc["AwayStat"]
            away_data = pd.concat([away_data, stats.to_frame().T])

        # print("\nFinal shapes:")
        # print("Home data:", home_data.shape)
        # print("Away data:", away_data.shape)

        # drop NA columns
        home_data = home_data.dropna(axis=1)
        away_data = away_data.dropna(axis=1)

        return {"home_data": home_data, "away_data": away_data}

    def calculate_statistics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate various statistics for numerical columns in the dataframe
        """
        # convert data to numeric where possible
        numeric_data = data.apply(pd.to_numeric, errors="ignore")
        numeric_cols = numeric_data.select_dtypes(include=["int64", "float64"]).columns

        # calculate statistics for each numeric column
        stats_dict = {}
        for col in numeric_cols:
            try:
                # get column data
                col_data = numeric_data[col]

                # basic statistics
                stats_dict[f"{col}_mean"] = col_data.mean()
                stats_dict[f"{col}_std"] = col_data.std() if len(col_data) > 1 else 0

                # calculate slope (trend)
                if len(col_data) > 1:
                    x = np.arange(len(col_data))
                    slope = np.polyfit(x, col_data, 1)[0]
                    stats_dict[f"{col}_trend"] = slope
                else:
                    stats_dict[f"{col}_trend"] = 0

            except Exception as e:
                print(f"Error calculating statistics for column {col}: {str(e)}")
                continue

        if not stats_dict:
            print("Warning: No statistics could be calculated")
            print("Data types:", data.dtypes)
            print("Data sample:", data.head())

        return pd.Series(stats_dict)

    def get_team_statistics(self, row: pd.Series) -> Dict[str, pd.DataFrame]:
        """
        Get statistics a row's  both home and away teams based on their last n matches
        """
        # get last n matches data
        last_n_data = self.get_last_n_data(row)

        # calculate statistics for both teams
        home_stats = self.calculate_statistics(last_n_data["home_data"])
        away_stats = self.calculate_statistics(last_n_data["away_data"])

        return {"home_stats": home_stats, "away_stats": away_stats}


class Process:
    def __init__(self, data: pd.DataFrame, all_home_stats=[], all_away_stats=[]):
        self.all_home_stats = all_home_stats
        self.all_away_stats = all_away_stats
        self.data = data
        self.match_info_df = self._get_match_info()

    def _get_match_info(self) -> pd.DataFrame:
        return self.data.loc["MatchInfo"]

    def process_all_match(self):
        """process each match one by one"""
        # initialize class that calculates the statistical variables for each row based on las n rows
        calc_stats = DataFrameStats(self.data, n=5)

        # iterate over eatch match
        for idx in self.match_info_df.index():
            try:
                match_stats = calc_stats.get_team_statistics(
                    self.match_info_df.loc[idx]
                )
                # store the stats
                self.all_home_stats.append(match_stats["home_stats"])
                self.all_away_stats.append(match_stats["away_stats"])
            except Exception as e:
                print(f"Error processing match {idx}: {str(e)}")
            continue
        return

    def final_dataframe(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """create final output file after processing te data"""

        # create final dataframes, training input X, with match indices
        self.all_home_stats = pd.DataFrame(
            self.all_home_stats, index=self.match_info_df.index
        )
        self.all_away_stats = pd.DataFrame(
            self.all_away_stats, index=self.match_info_df.index
        )

        # create labels based on goals (0: home win, 1: draw, 2: away win)
        self.match_info_df["label"] = np.where(
            self.match_info_df["HomeGoal"] > self.match_info_df["AwayGoal"],
            0,
            np.where(
                self.match_info_df["HomeGoal"] == self.match_info_df["AwayGoal"], 1, 2
            ),
        )

        # verify indices match are same across all df
        assert all(
            self.all_home_stats.index == self.match_info_df.index
        ), "Home stats indices don't match match info indices"
        assert all(
            self.all_away_stats.index == self.match_info_df.index
        ), "Away stats indices don't match match info indices"
        print("\nIndices verification passed: All DataFrames have matching indices")
        return

    def save_file(self, save_dir):
        """save the processed dataframes with row counts in filenames"""

        home_rows = len(self.all_home_stats)
        away_rows = len(self.all_away_stats)
        match_rows = len(self.match_info_df)

        # check directory and make math
        save_dir = Path(save_dir)
        save_dir.mkdir(exist_ok=True, parents=True)

        self.all_home_stats.to_csv(f"{save_dir}/home_stats_{home_rows}rows.csv")
        self.all_away_stats.to_csv(f"{save_dir}/away_stats_{away_rows}rows.csv")
        self.match_info_df.to_csv(
            f"{save_dir}/match_info_with_labels_{match_rows}rows.csv"
        )

        print(f"Files saved to {save_dir}!!")

        return


def main():
    json_path = "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/fbref/raw/trial90.json"
    config_path = (
        "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/config/config.yaml"
    )

    # convert json game data into multi-index dataframe
    ld_data = LoadData(json_path, config_path)
    data = ld_data.game_data_process()

    # process for mean, varience and slope data for each game, using data from last n games
    process_games = Process(data)
    process_games.process_all_match()
    process_games.final_dataframe()
    process_games.save_file(ld_data.config["out_dir"])


if __name__ == "__main__":
    main()
