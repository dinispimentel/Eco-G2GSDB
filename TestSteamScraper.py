import unittest
import sys
from SteamDB.SteamDBScraper import SteamDBScraper

from ecolib.price import Price
# from ecolib.logger import lg as logging


class MyTestCase(unittest.TestCase):
    def test_searchForTitle(self):

        appID = SteamDBScraper.searchForTitle("DayZ")
        self.assertNotEqual(appID, -1, "AppID não encontrado!")  # add assertion here

    def test_getLowestPrices(self):
        appID = SteamDBScraper.searchForTitle("DayZ")
        prices = SteamDBScraper.getLowestPrices(appID, lambda x: print(f"Trying to suspend 1 query: {x}"))
        self.assertIsInstance(prices[list(prices.keys())[0]][0], Price, "Não foi retornada uma instancia de Price debaixo de prices[0]")




if __name__ == '__main__':
    unittest.main()
