import json
from typing import Dict, List

import numpy as np
import pandas as pd
import yaml


def game_data_process(data: dict) -> pd.DataFrame:

    # flatten dataset
    home_stat_df = pd.json_normalize(data, record_path="HomeStat").drop_duplicates()
    away_stat_df = pd.json_normalize(data, record_path="AwayStat").drop_duplicates()
    game_data_df = pd.json_normalize(data, record_path="MatchInfo").drop_duplicates()

    # add first level index to make it multi-indexed
    home_stat_df.index = pd.MultiIndex.from_product([["HomeStat"], home_stat_df.index])
    away_stat_df.index = pd.MultiIndex.from_product([["AwayStat"], away_stat_df.index])
    game_data_df.index = pd.MultiIndex.from_product([["MatchInfo"], game_data_df.index])

    # concatenate data along the index to maintain separation of data
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

        # Debug print
        print("\nMatch info shape:", match_info.shape)
        print("Available teams:", match_info["HomeTeam"].unique())

        away_indices = match_info[
            (
                (match_info["HomeTeam"] == away_team)
                | (match_info["AwayTeam"] == away_team)
            )
            & (match_info.index != current_idx)  # Exclude current match
        ].index[: self.n]

        home_indices = match_info[
            (
                (match_info["HomeTeam"] == home_team)
                | (match_info["AwayTeam"] == home_team)
            )
            & (match_info.index != current_idx)  # Exclude current match
        ].index[: self.n]

        print(f"\nFound indices - Home: {home_indices}, Away: {away_indices}")

        # Get stats for home team's matches
        home_data = pd.DataFrame()
        for idx in home_indices:
            match_slice = self.data.xs(idx, level=1)
            if match_info.loc[idx, "HomeTeam"] == home_team:
                stats = match_slice.loc["HomeStat"]
            else:
                stats = match_slice.loc["AwayStat"]
            print(f"\nHome team stats shape for match {idx}:", stats.shape)
            home_data = pd.concat([home_data, stats.to_frame().T])

        # Get stats for away team's matches
        away_data = pd.DataFrame()
        for idx in away_indices:
            match_slice = self.data.xs(idx, level=1)
            if match_info.loc[idx, "HomeTeam"] == away_team:
                stats = match_slice.loc["HomeStat"]
            else:
                stats = match_slice.loc["AwayStat"]
            print(f"\nAway team stats shape for match {idx}:", stats.shape)
            away_data = pd.concat([away_data, stats.to_frame().T])

        print("\nFinal shapes:")
        print("Home data:", home_data.shape)
        print("Away data:", away_data.shape)

        # Drop NA columns
        home_data = home_data.dropna(axis=1)
        away_data = away_data.dropna(axis=1)

        return {"home_data": home_data, "away_data": away_data}

    def calculate_statistics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate various statistics for numerical columns in the dataframe
        """
        # Select only numeric columns
        numeric_cols = data.select_dtypes(include=["int64", "float64"]).columns

        # Calculate statistics for each numeric column
        stats_dict = {}
        for col in numeric_cols:
            col_data = data[col]

            # Basic statistics
            stats_dict[f"{col}_mean"] = col_data.mean()
            stats_dict[f"{col}_std"] = col_data.std()
            stats_dict[f"{col}_min"] = col_data.min()
            stats_dict[f"{col}_max"] = col_data.max()

            # Calculate slope (trend) using simple linear regression
            if len(col_data) > 1:
                x = np.arange(len(col_data))
                slope = np.polyfit(x, col_data, 1)[0]
                stats_dict[f"{col}_trend"] = slope
            else:
                stats_dict[f"{col}_trend"] = np.nan

        return pd.Series(stats_dict)

    def get_team_statistics(self, row: pd.Series) -> Dict[str, pd.DataFrame]:
        """
        Get statistics for both home and away teams based on their last n matches
        """
        # cet last n matches data
        last_n_data = self.get_last_n_data(row)

        # calculate statistics for both teams
        home_stats = self.calculate_statistics(last_n_data["home_data"])
        away_stats = self.calculate_statistics(last_n_data["away_data"])

        return {"home_stats": home_stats, "away_stats": away_stats}


def main():
    json_path = "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/fbref/trial90.json"

    # convert json to python dict
    data = open_json(json_path)

    # convert json game data into multi-index dataframe
    data = game_data_process(data)

    print("\nDataFrame structure:")
    print("Shape:", data.shape)
    print("\nIndex levels:", data.index.names)
    print("\nFirst few rows:")
    print(data.head())

    # Process Statistics
    stats = DataFrameStats(data, 5)

    # Initialize lists to store stats
    all_home_stats = []
    all_away_stats = []

    # Get match info rows
    match_info_df = data.loc["MatchInfo"]
    print("\nMatch info shape:", match_info_df.shape)

    # Process each match
    for idx in match_info_df.index:
        try:
            print(f"\nProcessing match index: {idx}")
            match_stats = stats.get_team_statistics(match_info_df.loc[idx])
            print("Stats calculated successfully")
            all_home_stats.append(match_stats["home_stats"])
            all_away_stats.append(match_stats["away_stats"])
        except Exception as e:
            print(f"Error processing match {idx}: {str(e)}")
            continue

    # Create final DataFrames with match indices
    all_home_stats_df = pd.DataFrame(all_home_stats, index=match_info_df.index)
    all_away_stats_df = pd.DataFrame(all_away_stats, index=match_info_df.index)

    print("\nHome stats DataFrame:")
    print(all_home_stats_df)
    print("\nAway stats DataFrame:")
    print(all_away_stats_df)


if __name__ == "__main__":
    main()
