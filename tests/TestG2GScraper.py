import unittest
from src.G2G.G2GScraper import G2GScraper
from src.G2G.G2GOfferBook import OfferBook
from src.G2G.G2GOffer import Offer


class G2GMainCase(unittest.TestCase):
    def test_G2GgetOffers(self):
        Offers = G2GScraper.getOffers(True)
        self.assertIsNotNone(Offers, "G2GScraper.getOffers retornou None")  # add assertion here
        self.assertIsInstance(Offers, OfferBook, "Não foi retornado um offer book")
        self.assertIsInstance(Offers.getOfferByIndex(0), Offer, "O Objeto dentro do OfferBook não é do género Offer")


    def test_G2GUpdateAccountCache(self):
        G2GScraper.updateAccountCache()
        with open("../src/cache/accounts-unfiltered.json", "r") as file :
            self.assertIsNotNone(file.read(), "Ficheiro vazio e o update nao o preencheu")



if __name__ == '__main__':
    unittest.main()
