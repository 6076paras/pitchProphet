"""
Module: stats
Description: This module provides classes for calculating statistics for the data.
"""


class StatisticsCalculator:
    """
    Class: StatisticsCalculator
    Description: This class provides methods for calculating various statistics for the data.
    """

    def __init__(self, data: pd.DataFrame, num_data: int):
        sellf.data = data
        self.num_data = num_data
