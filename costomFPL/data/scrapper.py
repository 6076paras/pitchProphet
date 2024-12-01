import sys

import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup


def make_URL(config):
    """
    Generate URL to scrape from:
    """
    print("Select data...")
    # TODO: add more catagories, promt error for invalid input
    season = input("Which season? [2024-2025, 2023-2022]: ")
    league = input("League? [Premier-League, Bundesliga]: ")

    if league == "Premier-League":
        league_id = "9"

    if league == "Bundesliga":
        league_id = "20"

    url = f"https://fbref.com/en/comps/{league_id}/{season}/schedule/{season}-{league}-Scores-and-Fixtures"
    return url, season, league


def soup_URL(url, season, league):
    """
    Collect links for every match in a season
    """
    # all links
    req_obj = requests.get(url)
    parse_html = BeautifulSoup(req_obj.content, "html.parser")
    all_links = parse_html.find_all("a")

    # links form score
    # TODO: check repetation
    relv_keys = [f"{league}", "/en/matches/"]
    match_links = []
    for link in all_links:
        href = link.get("href", "")
        if all(relv_key in href for relv_key in relv_keys):
            match_links.append("https://fbref.com" + href)
    return match_links


def test_pandas(config):
    for url in config["url"]:
        tables = pd.read_html(url)
        for table in tables:
            print(table.dtypes)
    return


def main():
    path = "/Users/paraspokharel/Programming/costomFPL/costomFPL/config/dataVars.yaml"
    with open(path, "r") as file:
        config = yaml.safe_load(file)
    url, league, season = (
        "https://fbref.com/en/comps/9/Premier-League/schedule/2023-2024-Premier_League-Scores-and-Fixtures",
        "Premier-League",
        "2024-2025",
    )
    print(soup_URL(url, season, league)[0:5])
    return


if __name__ == "__main__":
    main()
