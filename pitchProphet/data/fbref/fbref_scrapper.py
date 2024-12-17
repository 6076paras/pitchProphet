import json
import os
import random
import re
import sys
import time
from typing import Dict

import h5py
import numpy as np
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


def get_data(match_links, league, season, player_data=False):

    i = 0
    total_match = len(match_links)

    file_name = f"/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/fbref/{league}-{season}-{i}-matches.json"
    with open(
        file_name,
        "w",
    ) as json_file:

        json_file.write("[\n")

        for i, match_link in enumerate(match_links, start=1):
            print(f"Processing match {i}/{total_match}")
            tables = pd.read_html(match_link)

            # avaliable table data from the html page
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

            # Scrapp Game Data
            try:
                req_obj = requests.get(match_link)
                parse_html = BeautifulSoup(req_obj.content, "html.parser")
            except Exception as e:
                print(f"Error extracting table data for {match_link} : {e}")

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

            # match info
            match_info = {
                "Matchweek": int(match_week),
                "HomeTeam": str(teams[0].text),
                "AwayTeam": str(teams[1].text),
                "HomeGoal": int(home_goals),
                "AwayGoal": int(away_goals),
                "HomeXG": float(home_xG),
                "AwayXG": float(away_xG),
            }
            # Get last row (including headers)
            team_h_p = home_p_df.iloc[[-1], 5:].reset_index(drop=True)
            team_a_p = away_p_df.iloc[[-1], 5:].reset_index(drop=True)

            # Ensure to reset the column names
            team_h_p.columns = home_p_df.columns[5:]
            team_a_p.columns = away_p_df.columns[5:]

            # collect scrapped data
            dict_data = {
                "GameData": {
                    "MatchInfo": match_info,
                    "HomeStat": team_h_p,
                    "AwayStat": team_a_p,
                },
                "PlayerData": {
                    "HomeTeam": home_p_df,
                    "HomeTeamGK": home_gk_df,
                    "AwayTeam": away_p_df,
                    "AwayTeamGK": away_gk_df,
                },
            }

            # Store Data in JSON

            if player_data == False:

                # convert MatchInfo to df to ensure same format for json storage
                match_info = pd.DataFrame(match_info, index=[0])
                # convert df to dict
                dict_data["GameData"]["MatchInfo"] = match_info.to_dict(
                    orient="records"
                )
                dict_data["GameData"]["AwayStat"] = dict_data["GameData"][
                    "AwayStat"
                ].to_dict(orient="records")
                dict_data["GameData"]["HomeStat"] = dict_data["GameData"][
                    "HomeStat"
                ].to_dict(orient="records")

                # dump
                json.dump(dict_data["GameData"], json_file, indent=4)
                if i < total_match:
                    json_file.write(",\n")

                # make file name unique
                current_name = f"/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/fbref/{league}-{season}-{i - 1}-matches.json"
                new_name = f"/Users/paraspokharel/Programming/pitchProphet/pitchProphet/data/fbref/{league}-{season}-{i}-matches.json"
                os.rename(current_name, new_name)

            time.sleep(random.uniform(5, 10))

        json_file.write("\n]")

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


# TODO: only keep files with largest match data
def del_json():
    pass


def main():
    path = (
        "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/config/config.yaml"
    )
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
