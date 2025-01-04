from typing import Dict

import numpy as np
import pandas as pd


class DescriptiveStats:
    """
    Class to calculate and return descriptive statistics such as mean, variance
    and slope for each row (match), using last n team features
    for both home and away teams separately.

    Attributes:
        data (pd.DataFrame): DataFrame containing match data obtained
            from LoadData class.
        n (int): Number of previous matches to consider to calculate
            descriptive statistics - such as mean, variance and slope.
        inference (bool): Whether to use the class for inference or training data.

    Methods:
        process_home_away_features(row: pd.Series, inference=False) -> Dict[str, pd.Series]:
            Returns descriptive statistics for a match by calling
            _calculate_statistics() using home and away team data from
            _get_last_n_data().
    """

    def __init__(self, data: pd.DataFrame, last_n_match=5, inference=False):
        self.data = data
        self.last_n_match = last_n_match
        self.inference = inference

    def _standardize_team_name(self, team_name: str) -> str:
        """standardizes team names to match between fixtures and match data."""
        team_mapping = {
            "Newcastle Utd": "Newcastle United",
            "Nott'ham Forest": "Nottingham Forest",
            "Manchester Utd": "Manchester United",
            "Tottenham": "Tottenham Hotspur",
        }
        return team_mapping.get(team_name, team_name)

    def _get_last_n_data(self, row: pd.Series) -> Dict[str, pd.DataFrame]:
        """retrieves last n matches' home team features and away team features.
        For training: uses inner index from MatchInfo outer index to access home and away team's
        features for last n games before the current match.
        For inference: gets the n matches for teams specified in the fixtures."""

        match_info = self.data.loc["MatchInfo"]

        if self.inference:
            # For inference mode, use the team names from fixtures
            home_team = self._standardize_team_name(row["Home"])
            away_team = self._standardize_team_name(row["Away"])
            current_idx = None  # No need to filter by index in inference mode
        else:
            # For training mode, use team names from match info
            home_team = row["HomeTeam"]
            away_team = row["AwayTeam"]
            current_idx = row.name

        print(f"\nProcessing match: Home={home_team} vs Away={away_team}")
        if current_idx is not None:
            print(f"Current index: {current_idx}")

        # Get indices for matches where teams played
        if self.inference:
            # For inference, get the last n matches without index filtering
            home_indices = match_info[
                (match_info["HomeTeam"] == home_team)
                | (match_info["AwayTeam"] == home_team)
            ].index[: self.last_n_match_last_match]
            away_indices = match_info[
                (match_info["HomeTeam"] == away_team)
                | (match_info["AwayTeam"] == away_team)
            ].index[: self.last_n_match]
        else:
            # For training, get only matches before the current index
            home_indices = match_info[
                (
                    (match_info["HomeTeam"] == home_team)
                    | (match_info["AwayTeam"] == home_team)
                )
                & (match_info.index < current_idx)
            ].index[: self.last_n_match]
            away_indices = match_info[
                (
                    (match_info["HomeTeam"] == away_team)
                    | (match_info["AwayTeam"] == away_team)
                )
                & (match_info.index < current_idx)
            ].index[: self.last_n_match_last_match]

        print(f"Found {len(home_indices)} matches for {home_team}")
        print(f"Found {len(away_indices)} matches for {away_team}")

        # Get stats for home team's matches
        home_data = pd.DataFrame()
        for idx in home_indices:
            match_slice = self.data.xs(idx, level=1)
            if match_info.loc[idx, "HomeTeam"] == home_team:
                stats = match_slice.loc["HomeStat"]
            else:
                stats = match_slice.loc["AwayStat"]
            home_data = pd.concat([home_data, stats.to_frame().T])

        # Get stats for away team's matches
        away_data = pd.DataFrame()
        for idx in away_indices:
            match_slice = self.data.xs(idx, level=1)
            if match_info.loc[idx, "HomeTeam"] == away_team:
                stats = match_slice.loc["HomeStat"]
            else:
                stats = match_slice.loc["AwayStat"]
            away_data = pd.concat([away_data, stats.to_frame().T])

        # Drop NA columns
        home_data = home_data.dropna(axis=1)
        away_data = away_data.dropna(axis=1)

        return {"home_data": home_data, "away_data": away_data}

    def _calculate_statistics(self, data: pd.DataFrame) -> pd.Series:
        """computes (descriptive) statistical metrics for all features
        using input table of last n game's features."""

        # convert data to numeric where possible
        try:
            numeric_data = data.apply(pd.to_numeric)
            numeric_cols = numeric_data.select_dtypes(
                include=["int64", "float64"]
            ).columns
        except ValueError as e:
            print(f"Error converting column {col} to numeric: {str(e)}")

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

    def process_home_away_features(
        self, row: pd.Series, inference=False
    ) -> Dict[str, pd.Series]:
        """get descriptive statistics for a match for both home and away team"""

        # get last n matches data
        last_n_data = self._get_last_n_data(row)

        # calculate statistics for both teams
        home_stats = self._calculate_statistics(last_n_data["home_data"])
        away_stats = self._calculate_statistics(last_n_data["away_data"])

        return {"home_stats": home_stats, "away_stats": away_stats}
