import json
import re
import sys

import h5py
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


def get_data(match_links, league, season):
    with open(f"costomFPL/data/FBRef-{league}-{season}.json", "w") as json_file:
        for match_link in match_links:
            tables = pd.read_html(match_link)

            # player data
            home_p_df = tables[3]
            home_p_df.columns = home_p_df.columns.droplevel(0)
            home_gk_df = tables[9]
            home_gk_df.columns = home_gk_df.columns.droplevel(0)
            away_p_df = tables[10]
            away_p_df.columns = away_p_df.columns.droplevel(0)
            away_gk_df = tables[16]
            away_gk_df.columns = away_gk_df.columns.droplevel(0)

            # store in json
            data_dict = {
                "Home Team": {
                    "Player Data": home_p_df.to_dict(orient="records"),
                    "Goalkeeper Data": home_gk_df.to_dict(orient="records"),
                },
                "Away Team": {
                    "Player Data": away_p_df.to_dict(orient="records"),
                    "Goalkeeper Data": away_gk_df.to_dict(orient="records"),
                },
            }
            json.dump(data_dict, json_file, indent=4)

        # TODO: game data

        # pattern = r"/en/matches/([a-f0-9]+)/(.*?)-(.*?)-(\w+\s\d{1,2}-\d{4})"
        # match = re.search(pattern, match_link)

        # if match:
        #     match_id = match.group(1)
        #     home_team = match.group(2)
        #     away_team = match.group(3)
        #     date = match.group(4)

        # game_df = pd.DataFrame(
        #     {"Home team": home_team, "Away team": away_team, "Date": date}
        # )
    return


def main():
    path = "/Users/paraspokharel/Programming/costomFPL/costomFPL/config/dataVars.yaml"
    with open(path, "r") as file:
        config = yaml.safe_load(file)
    url, league, season = (
        "https://fbref.com/en/comps/9/2023-2024/schedule/2023-2024-Premier-League-Scores-and-Fixtures",
        "Premier-League",
        "2023-2024",
    )
    get_data(soup_URL(url, season, league), season, league)
    return


if __name__ == "__main__":
    main()
