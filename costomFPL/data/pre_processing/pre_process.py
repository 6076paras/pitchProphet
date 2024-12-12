import pandas as pd
import yaml


def load_data(path: str) -> pd.DataFrame:
    """
    Loads json file into pd.Dataframe
    """
    return pd.read_csv(path)


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
    json_path = "/Users/paraspokharel/Programming/costomFPL/costomFPL/data/fbref/2023-2024-Premier-League-76-matches.json"
    print(pd.json_normalize(json_path))


if __name__ == "__main__":
    main()
