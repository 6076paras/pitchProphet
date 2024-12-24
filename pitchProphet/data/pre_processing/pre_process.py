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

from pitchProphet.data.pre_processing.load_data import LoadData
from pitchProphet.data.pre_processing.process import Process


def main():
    json_path = "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/fbref/raw/trial90.json"
    config_path = (
        "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/config/config.yaml"
    )

    # convert json game data into multi-index dataframe
    ld_data = LoadData(json_path, config_path)
    data = ld_data.game_data_process()

    # Process Data
    process_games = Process(data)

    # calculate for mean, varience and slope data for each game and its column header, using data from last n games
    process_games.process_all_match()

    # save the data as 3 separate files -> one for general game information, one for away team stat and one for home team stat
    process_games.final_dataframe()
    process_games.save_file(ld_data.config["out_dir"])


if __name__ == "__main__":
    main()
