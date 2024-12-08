import pandas as pd


def load_data(files, config):
    """
    Loads .csv files and returns df object with relevent variables
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


def main():
    print("Test")
    path = "/Users/paraspokharel/Programming/costomFPL/costomFPL/config/dataVars.yaml"
    with open(path, "r") as file:
        config = yaml.safe_load(file)
    return


if __name__ == "__main__":
    main()
