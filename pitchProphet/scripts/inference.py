import pandas as pd
import yaml

from pitchProphet.data.fbref.fbref_scrapper import FBRefScraper


def get_fixtures(match_week, url):
    """
    Returns a fixture list from FBRef
    """

    all_fixtures = pd.read_html(url)
    week_fixtures = all_fixtures[0][all_fixtures[0]["Wk"] == match_week]
    team_list = week_fixtures[["Home", "Away"]].reset_index()
    team_list.name = f"Matchweek {match_week}"
    return team_list


def main():
    config_path = (
        "/Users/paraspokharel/Programming/pitchProphet/pitchProphet/config/config.yaml"
    )
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    config = config["scraper"]
    league = "Premier-League"
    league_id = config["league_ids"][league]
    url = f"{config["base_url"]}/{league_id}/2024-2025/schedule/2024-2025-{league}-Scores-and-Fixtures"
    print(get_fixtures(1, url))


if __name__ == "__main__":
    main()
