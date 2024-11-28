import pandas as pd

# import requests
import yaml

# from bs4 import BeautifulSoup


def returnURL(config):
    return NotImplemented


def test_pandas(config):
    for url in config["url"]:
        data = pd.read_html(url)
        print(data[0])
    return


if __name__ == "__main__":

    path = (
        "/Users/paraspokharel/Programming/costomFPL/" "costomFPL/config/dataVars.yaml"
    )
    with open(path, "r") as file:
        config = yaml.safe_load(file)

    a = test_pandas(config)
