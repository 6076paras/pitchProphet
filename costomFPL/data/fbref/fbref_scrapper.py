import json
import os
import random
import re
import sys
import time

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

    total_match = len(match_links)
    i = 0
    # Initialize list for h5file's subgroup -> 3 groups for global game stat, 4 group for local player stat
    m_g_list = []
    m_a_list = []
    m_h_list = []
    p_a_l = []
    p_h_l = []
    gk_a_l = []
    gk_h_l = []

    file_name = f"/Users/paraspokharel/Programming/costomFPL/costomFPL/data/fbref/{league}-{season}-{i}-matches.h5"
    with h5py.File(
        file_name,
        "w",
    ) as h5_file:

        try:
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

                # Extract Game Data

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

                # Convert To Numpy Struct Array

                # toal team stats
                team_h_p = home_p_df.iloc[-1, 5:].to_frame().T.to_records(index=True)
                team_a_p = away_p_df.iloc[-1, 5:].to_frame().T.to_records(index=True)

                # team general data
                g_data = {
                    "Matchweek": int(match_week),
                    "HomeTeam": str(teams[0].text),
                    "AwayTeam": str(teams[1].text),
                    "HomeGoal": int(home_goals),
                    "AwayGoal": int(away_goals),
                    "HomeXG": float(home_xG),
                    "AwayXG": float(away_xG),
                }
                game_data = pd.DataFrame([g_data]).to_records(index=True)

                # TODO: Clean later!
                # datatype for h5 handeling
                new_type = np.dtype(
                    [
                        ("index", "<i8"),
                        ("Matchweek", "<i8"),
                        ("HomeTeam", "<S10"),
                        ("AwayTeam", "<S10"),
                        ("HomeGoal", "<i8"),
                        ("AwayGoal", "<i8"),
                        ("HomeXG", "<f8"),
                        ("AwayXG", "<f8"),
                    ]
                )
                game_data = game_data.astype(new_type)

                # player data
                if player_data == True:
                    h_p = home_p_df.iloc[:-1].to_frame().T.to_records(index=True)
                    a_p = away_p_df.iloc[:-1].to_frame().T.to_records(index=True)
                    home_gk = home_gk_df.to_frame().T.to_records(index=True)
                    away_gk = away_gk_df.to_frame().T.to_records(index=True)

                # Make List for H5 Dataset

                # global stat
                m_g_list.append(game_data)
                m_a_list.append(team_a_p)
                m_h_list.append(team_h_p)

                # player stat
                if player_data == True:
                    p_a_l.append(a_p)
                    p_h_l.append(h_p)
                    gk_a_l.append(home_gk)
                    gk_h_l.append(away_gk)

                # make file name unique
                current_name = f"/Users/paraspokharel/Programming/costomFPL/costomFPL/data/fbref/{league}-{season}-{i - 1}-matches.h5"
                new_name = f"/Users/paraspokharel/Programming/costomFPL/costomFPL/data/fbref/{league}-{season}-{i}-matches.h5"
                os.rename(current_name, new_name)

                time.sleep(random.uniform(5, 10))

                if i == 1:
                    break

        except Exception as e:
            print(f"Error extracting table data for {match_link} : {e}")

        # Write to H5 File

        # convert to numpy
        game_a = np.concatenate(m_g_list)
        print(
            f"""frist element:{game_a[0]}
        Array: {game_a}
        Datatype: {game_a[0].dtype}"""
        )
        game_h_p_a = np.concatenate(m_h_list)
        game_a_p_a = np.concatenate(m_a_list)
        if player_data == True:
            p_a_a = np.concatenate(p_a_l)
            p_h_a = np.concatenate(p_h_l)
            gk_a_a = np.concatenate(gk_a_l)
            gk_h_a = np.concatenate(gk_h_l)

        # TODO: create subgroup instead??
        # write
        team = h5_file.create_group("team_data")
        player = h5_file.create_group("player_data")

        team.create_dataset("game_info", data=game_a)
        team.create_dataset("home_team", data=game_h_p_a)
        team.create_dataset("away_team", data=game_a_p_a)

        if player_data == True:
            player.create_dataset("home_players", data=p_h_a)
            player.create_dataset("away_players", data=p_h_a)
            player.create_dataset("home_gk", data=gk_h_a)
            player.create_dataset("away_gk", data=gk_a_a)

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


# TODO: only keep json with largest match data
def del_json():
    pass


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
