import numpy as np
import pandas as pd
import pytest


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
