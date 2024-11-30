import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup


def make_URL(config):
    """
    Generate URL to scrape from:
    """
    print("Select data...")
    season = input("Which season? [2024-2025, 2023-2022]: ")
    league = input("League? [Premier League, Bundesliga]: ")
    return season, league


def test_pandas(config):
    for url in config["url"]:
        tables = pd.read_html(url)
        for table in tables:
            print(table.dtypes)
    return


if __name__ == "__main__":
    path = "/Users/paraspokharel/Programming/costomFPL/costomFPL/config/dataVars.yaml"
    with open(path, "r") as file:
        config = yaml.safe_load(file)
    make_URL(config)
