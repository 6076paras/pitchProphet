from typing import Dict

import numpy as np
import pandas as pd


class DescriptiveStats:
    """
    Class to calculate and return descriptive statistics such as mean, varience
    and slope for reach row (match), using last n team features
    for both home and away teams separately.

    Attributes:
        data (pd.DataFrame): DataFrame containing match data obtained
            from LoadData class.
        n (int): Number of previous matches to consider to calculate
            descriptive statiscics - such as mean, variaence and slope.

    Methods:
        process_home_away_features(row: pd.Series) -> Dict[str, pd.Series]:
            Returns descriptive statistics for a match by calling
            _calculate_statisctics() using home and away team data from
            _get_last_n_data().

    """

    def __init__(self, data: pd.DataFrame, n=5):
        self.data = data
        self.n = n

    def _get_last_n_data(self, row: pd.Series) -> Dict[str, pd.DataFrame]:
        """retrieves last n matches' home team features and away team features.
        it uses inner index from MatchInfo outer index to acess home and away team's
        features for last n games."""

        # get team names from the match info
        home_team = row["HomeTeam"]
        away_team = row["AwayTeam"]
        current_idx = row.name

        print(f"\nProcessing match: Home={home_team} vs Away={away_team}")
        print(f"Current index: {current_idx}")

        # get all match indices where teams played
        match_info = self.data.loc["MatchInfo"]

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

        # drop NA columns
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

    def process_home_away_features(self, row: pd.Series) -> Dict[str, pd.DataFrame]:
        """get descriptive statistics for a match for both home and away team"""

        # get last n matches data
        last_n_data = self._get_last_n_data(row)

        # calculate statistics for both teams
        home_stats = self._calculate_statistics(last_n_data["home_data"])
        away_stats = self._calculate_statistics(last_n_data["away_data"])

        return {"home_stats": home_stats, "away_stats": away_stats}
