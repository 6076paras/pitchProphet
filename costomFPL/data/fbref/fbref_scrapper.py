import json
import re
import time

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

    total_match = len(match_links)
    with open(
        f"/Users/paraspokharel/Programming/costomFPL/costomFPL/data/fbref/{league}-{season}.json",
        "w",
    ) as json_file:

        try:
            for i, match_link in enumerate(match_links, start=1):
                print(f"Processing match {i}/{total_match}")
                tables = pd.read_html(match_link)
                # player data
                home_p_df = tables[3]
                home_p_df.columns = home_p_df.columns.droplevel(0)
                home_p_df = home_p_df.loc[:, ~home_p_df.columns.duplicated()]

                home_gk_df = tables[9]
                home_gk_df.columns = home_gk_df.columns.droplevel(0)
                home_gk_df = home_gk_df.loc[:, ~home_gk_df.columns.duplicated()]

                away_p_df = tables[10]
                away_p_df.columns = away_p_df.columns.droplevel(0)
                away_p_df = away_p_df.loc[:, ~away_p_df.columns.duplicated()]

                away_gk_df = tables[16]
                away_gk_df.columns = away_gk_df.columns.droplevel(0)
                away_gk_df = away_gk_df.loc[:, ~away_gk_df.columns.duplicated()]

                # extract game data
                req_obj = requests.get(match_link)
                parse_html = BeautifulSoup(req_obj.content, "html.parser")

                match_week = parse_html.find(string=re.compile(r"Matchweek \d+"))
                match_week = re.sub(r"\D", "", match_week)

                # xg from class="score_xg"
                xG = parse_html.find_all(class_="score_xg")
                home_xG = xG[0].text
                away_xG = xG[1].text

                # goals from class="score"
                goals = parse_html.find_all(class_="score")
                home_goals = goals[0].text
                away_goals = goals[1].text

                # team names from class="scorebox" strong anchor
                teams = parse_html.select(".scorebox strong a")

                data_dict = {
                    "GameData": {
                        "Matchweek": int(match_week),
                        "HomeTeam": teams[0].text,
                        "AwayTeam": teams[1].text,
                        "HomeGoal": int(home_goals),
                        "AwayGoal": int(away_goals),
                        "HomeXG": float(home_xG),
                        "AwayXG": float(away_xG),
                    },
                    "PlayerData": {
                        "HomeTeam": home_p_df.to_dict(orient="records"),
                        "HomeTeamGK": home_gk_df.to_dict(orient="records"),
                        "AwayTeam": away_p_df.to_dict(orient="records"),
                        "AwayTeamGK": away_gk_df.to_dict(orient="records"),
                    },
                }
                json.dump(data_dict, json_file, indent=4)
                time.sleep(3)
        except Exception as e:
            print(f"Error extracting table data for {match_link} : {e}")
    return


def get_fixtures(match_week, league=None):
    """
    Returns a fixture list from FBRef
    """
    url = "https://fbref.com/en/comps/9/2023-2024/schedule/2023-2024-Premier-League-Scores-and-Fixtures"
    all_fixtures = pd.read_html(url)
    week_fixtures = all_fixtures[0][all_fixtures[0]["Wk"] == match_week]
    team_list = week_fixtures[["Home", "Away"]].reset_index()
    team_list.name = f"Matchweek {match_week}"
    return team_list


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
