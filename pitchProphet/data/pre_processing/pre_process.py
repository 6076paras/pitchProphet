"""
Pre-processing module for soccer match data.

This module serves as the main entry point for processing football match statistics from raw data.
It implements a pipeline that:
1. Loads raw match data from JSON files using the LoadData class
2. Processes the data to calculate statistical features using the Process class which further is depended on DescriptiveStats class
3. Saves the processed data as separate CSV files for home team stats, away team stats,
   and general match information with outcome labels
"""

from pitchProphet.data.pre_processing.load_data import LoadData
from pitchProphet.data.pre_processing.process import Process


def main() -> None:

    json_path = (
        "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/fbref/raw"
    )
    config_path = (
        "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/config/config.yaml"
    )

    # convert json game data into multi-indexed dataframe
    ld_data = LoadData(json_path, config_path)
    data = ld_data.game_data_process()

    # calculate descriptive stats  for all matches
    process_games = Process(data)
    process_games.process_all_match()

    # save processed data into 2 separate files
    # one with general game information for y label and other 2 home home and
    # away teams descriptive statiscs for all features to be used as x variable for training
    process_games.final_dataframe()
    process_games.save_file(ld_data.config["out_dir"])


if __name__ == "__main__":
    main()
