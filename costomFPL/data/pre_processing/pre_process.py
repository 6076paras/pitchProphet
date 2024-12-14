import json

import pandas as pd
import yaml


def flattan_json(path: str) -> pd.DataFrame:
    """
    Loads json file into pd.Dataframe
    return pd.read_csv(path)
    by flattening.
    """
    pass


def calc_stats(n, data):
    """
    Dataframe map that generates statistics, f(data_i) using last its last n
    values
    """
    # standard deviation

    # mean

    # slope

    pass


def extract_relv(data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract relevent data
    """
    pass


def main():
    json_path = "/Users/paraspokharel/Programming/costomFPL/costomFPL/data/fbref/2023-2024-Premier-League-10-matches.json"
    with open(json_path, "r") as file:
        data = json.load(file)
    normalized = pd.json_normalize(data)
    print(normalized.columns)


if __name__ == "__main__":
    main()
