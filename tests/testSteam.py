from src.G2G.G2GOfferBook import OfferBook
from src.SteamDB.SteamDBScraper import SteamDBScraper
from src.config import Config

# game = "Factorio"
# appID = SteamDBScraper.searchForTitle(game)

# for price in SteamDBScraper.getLowestPrices(appID, base="EUR"):
#     print(game + ": " + str(price.value) + str(price.currency) + " | " + "{:.2f}".format(float(price.cValue)) +
#           str(price.cCurrency))


ob = OfferBook.loadFromFile(Config.OfferBooking.FILES.getPriced(testing=True))

ob.print()

SteamDBScraper.setOfferBookAppIDs(ob)

with open("../src/cache/offer-book-priced-appided.json", "w") as f:
    f.write(ob.toJSON())

