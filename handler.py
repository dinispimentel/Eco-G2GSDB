from G2G.G2GScraper import G2GScraper
from SteamDB.SteamDBScraper import SteamDBScraper


class G2GSteamDBHandler:

    @staticmethod
    def getPriceComparisonG2GSteam(offerbook):
        # Offerbook : <title> = {
        #   path = "<path>",
        #   ...
        # }

        for offer in offerbook.offers:
            app_id = SteamDBScraper.searchForTitle(offer.title)
            SteamDBScraper

