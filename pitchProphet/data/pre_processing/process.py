from pathlib import Path

import numpy as np
import pandas as pd

from pitchProphet.data.pre_processing.calculate_stats import DescriptiveStats


class Process:
    """
    Class for processing all football match data to add descriptive statistics.

    This class iterates over all matches, applying the `process_home_away_features`
    method from the `DescriptiveStats` class to calculate statistics for each match.
    It generates a processed DataFrame separately for all home team statistics,
    all away team statistics saves those separatly. This is used as x variable for training.
    It also saves a separete file that has general game information that can be used as
    y label variable for training.

    Attributes:
        data (pd.DataFrame): DataFrame containing all match data.


    Methods:
        process_all_match() -> None:
            Calculates and stores statistics for each match.

        final_dataframe() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
            Generates final DataFrames with match outcome labels.

        save_file(save_dir: str) -> None:
            Saves processed DataFrames to CSV files in the specified directory.
    """

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
        calc_stats = DescriptiveStats(self.data, n=5)

        # TODO: dont process the first 5 matchweeks and remove the first five matchweek from the match_info_df
        # iterate over eatch match
        for idx in self.match_info_df.index:
            try:
                match_stats = calc_stats.process_home_away_features(
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
        # drop n/a
        self.match_info_df = self.match_info_df.dropna(axis=1)

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
