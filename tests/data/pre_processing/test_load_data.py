from pathlib import Path

import pandas as pd
import pytest

from pitchProphet.data.pre_processing.load_data import LoadData


@pytest.fixture
def load_data(mock_config):
    """fixture to provide load data instance"""
    return LoadData(mock_config, inference=True)


def test_initialization(load_data, mock_config):
    """test constructor and configuration loading"""
    pass


def test_open_yaml(load_data):
    """test yaml configuration file loading"""
    pass


def test_find_relevant_files(load_data):
    """test finding relevant json files based on league and matchweek"""
    pass


def test_open_json(load_data):
    """test json data loading functionality"""
    pass


def test_game_data_process(load_data):
    """test processing of game data into dataframe"""
    pass


def test_inference_mode(mock_config):
    """test behavior in inference mode"""
    pass


def test_player_data_mode(mock_config):
    """test behavior with player data enabled"""
    pass


def test_league_filtering(load_data):
    """test filtering data by league"""
    pass


def test_matchweek_filtering(load_data):
    """test filtering data by matchweek"""
    pass


def test_data_structure(load_data):
    """test structure of processed dataframe"""
    pass


def test_error_handling(load_data):
    """test error handling for various scenarios"""
    pass


def test_file_path_construction(load_data):
    """test construction of file paths"""
    pass


def test_data_validation(load_data):
    """test validation of loaded data"""
    pass
