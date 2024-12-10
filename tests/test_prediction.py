import numpy as np
import pandas as pd
import pytest


def generate_ml_out():
    home_team_names = [
        "Manchester United",
        "Liverpool",
        "Chelsea",
        "Arsenal",
        "Tottenham",
        "Manchester City",
        "Leicester City",
        "Everton",
        "West Ham",
        "Aston Villa",
    ]
    away_team_names = [
        "Arsenal",
        "Chelsea",
        "Manchester United",
        "Liverpool",
        "Leicester City",
        "Tottenham",
        "Everton",
        "West Ham",
        "Aston Villa",
        "Southampton",
    ]

    np.random.seed(0)
    home_win_prob = np.random.rand(10)
    away_win_prob = np.random.rand(10)
    draw_prob = 1 - home_win_prob - away_win_prob

    home_win_prob = np.clip(home_win_prob, 0, 1)
    away_win_prob = np.clip(away_win_prob, 0, 1)
    draw_prob = np.clip(draw_prob, 0, 1)

    df = pd.DataFrame(
        {
            "Home Team": home_team_names,
            "Away Team": away_team_names,
            "p(Home Team)": home_win_prob,
            "p(Away Team)": away_win_prob,
            "p(Draw)": draw_prob,
        }
    )

    return df


# Test 1: Check if the generated data has the expected number of rows and columns
def test_shape():
    df = generate_match_data()
    assert df.shape == (10, 5), "DataFrame should have 10 rows and 5 columns"


# Test 2: Check if probabilities sum to 1 for each row
def test_probabilities_sum():
    df = generate_match_data()
    for index, row in df.iterrows():
        total_probability = (
            row["Home Team Win Probability"]
            + row["Away Team Win Probability"]
            + row["Draw Probability"]
        )
        assert np.isclose(
            total_probability, 1
        ), f"Probabilities for row {index} do not sum to 1"


# Test 3: Ensure column data types are correct
def test_data_types():
    df = generate_match_data()
    assert (
        df["Home Team Name"].dtype == object
    ), "Home Team Name should be of type object (string)"
    assert (
        df["Away Team Name"].dtype == object
    ), "Away Team Name should be of type object (string)"
    assert (
        df["Home Team Win Probability"].dtype == float
    ), "Home Team Win Probability should be of type float"
    assert (
        df["Away Team Win Probability"].dtype == float
    ), "Away Team Win Probability should be of type float"
    assert (
        df["Draw Probability"].dtype == float
    ), "Draw Probability should be of type float"
