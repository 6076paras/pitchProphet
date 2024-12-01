import unittest

from scrapper import soup_URL


class TestScrapper(unittest.TestCase):
    def test_soup_URL(self):
        # Test case 1: Valid URL, season, and league
        url = "https://example.com"
        season = "2021"
        league = "Premier League"
        result = soup_URL(url, season, league)
        self.assertIsNotNone(result)
        # Add more assertions to validate the result if needed

        # Test case 2: Invalid URL
        url = "invalid_url"
        season = "2021"
        league = "Premier League"
        with self.assertRaises(Exception):
            soup_URL(url, season, league)

        # Test case 3: Invalid season
        url = "https://example.com"
        season = "invalid_season"
        league = "Premier League"
        with self.assertRaises(Exception):
            soup_URL(url, season, league)

        # Test case 4: Invalid league
        url = "https://example.com"
        season = "2021"
        league = "invalid_league"
        with self.assertRaises(Exception):
            soup_URL(url, season, league)


if __name__ == "__main__":
    unittest.main()
