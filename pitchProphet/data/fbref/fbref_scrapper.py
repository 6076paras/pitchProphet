import json
import logging
import os
import random
import re
import time

import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup


class FBRefScraper:
    def __init__(self, config_path, player_data=False):
        # load config file
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.config = config["scraper"]
        self.player_data = player_data

        # setup basic logging
        logging.basicConfig(level=logging.INFO)

    def get_match_links(self, url, league):
        """get all match links from the season page"""
        try:
            # handle rate limiting
            for attempt in range(3):
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    break
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:  # too Many Requests
                        wait_time = 60 * (attempt + 1)
                        print(f"\nRate limited. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    raise

            # find match links
            soup = BeautifulSoup(response.content, "html.parser")
            all_links = soup.find_all("a")

            # filter relevant links
            match_links = []
            for link in all_links:
                href = link.get("href", "")
                if league in href and "/en/matches/" in href:
                    match_links.append("https://fbref.com" + href)

            return match_links

        except Exception as e:
            print(f"Error getting match links: {e}")
            raise

    def scrape_match(self, match_link):
        """scrape data for a single match"""
        try:
            # get tables from the page
            tables = pd.read_html(match_link)

            # process team stats
            home_stats = self._process_team_stats(tables[3], tables[9])
            away_stats = self._process_team_stats(tables[10], tables[16])

            # get match info
            response = requests.get(match_link)
            soup = BeautifulSoup(response.content, "html.parser")

            # get basic match info
            match_week = soup.find(string=re.compile(r"Matchweek \d+"))
            match_week = int(re.sub(r"\D", "", match_week))

            xg = soup.find_all(class_="score_xg")
            goals = soup.find_all(class_="score")
            teams = soup.select(".scorebox strong a")

            match_info = {
                "Matchweek": match_week,
                "HomeTeam": str(teams[0].text),
                "AwayTeam": str(teams[1].text),
                "HomeGoal": int(goals[0].text),
                "AwayGoal": int(goals[1].text),
                "HomeXG": float(xg[0].text),
                "AwayXG": float(xg[1].text),
            }

            game_data = {
                "MatchInfo": match_info,
                "HomeStat": home_stats["TeamStat"].to_dict("records"),
                "AwayStat": away_stats["PlayerStat"].to_dict("records"),
            }
            if self.player_data == True:
                game_data["HomePlayersStat"] = (
                    home_stats["PlayerStat"].to_dict("records"),
                )
                game_data["AwayPlayersStat"] = (
                    away_stats["PlayerStat"].to_dict("records"),
                )
                game_data["HomeGKStat"] = (home_stats["GKStat"].to_dict("records"),)
                game_data["AwayGKStat"] = (away_stats["GKStat"].to_dict("records"),)

            return game_data

        except Exception as e:
            print(f"Error scraping match {match_link}: {e}")
            raise

    def _process_team_stats(self, player_df, gk_df):
        """process team statistics"""
        # clean up column names
        player_df.columns = player_df.columns.droplevel(0)
        player_df = player_df.loc[:, ~player_df.columns.duplicated()]

        gk_df.columns = gk_df.columns.droplevel(0)
        gk_df = gk_df.loc[:, ~gk_df.columns.duplicated()]

        team_df = player_df.iloc[[-1], 5:].reset_index(drop=True)
        player_df = player_df.iloc[:-1]

        return {"TeamStat": team_df, "PlayerStat": player_df, "GKStat": gk_df}

    def scrape_season(self, season, league):
        """scrape all matches in a season"""
        # make url
        league_id = self.config["league_ids"][league]
        url = f"{self.config['base_url']}/{league_id}/{season}/schedule/{season}-{league}-Scores-and-Fixtures"

        # get all match links
        match_links = self.get_match_links(url, league)
        total_matches = len(match_links)
        print(f"Found {total_matches} matches to scrape")

        # scrape each match
        all_matches = []
        for i, link in enumerate(match_links, 1):
            try:
                print(f"\nProcessing {i}/{total_matches} matches")
                match_data = self.scrape_match(link)
                all_matches.append(match_data)

                # wait between requests
                sleep_time = random.uniform(*self.config["sleep_range"])
                time.sleep(sleep_time)

                if i == 3:
                    break

            except Exception as e:
                print(f"Error on match {i}: {e}")
                continue

        # create output directory if it doesn't exist
        os.makedirs(self.config["output_dir"], exist_ok=True)

        # save data
        output_file = f"{self.config['output_dir']}/{league}-{season}-{len(all_matches)}-matches.json"
        with open(output_file, "w") as f:
            json.dump(all_matches, f, indent=4)
        print(f"\nSaved {len(all_matches)} matches to {output_file}")


def main():
    try:
        config = "pitchProphet/config/config.yaml"
        scraper = FBRefScraper(config)
        scraper.scrape_season("2020-2021", "Premier-League")
    except Exception as e:
        print(f"Error in main process: {e}")
        raise


if __name__ == "__main__":
    main()
