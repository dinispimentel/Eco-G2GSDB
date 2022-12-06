from G2G.G2GOfferBook import OfferBook
from SteamDB.SteamDBScraper import SteamDBScraper
from config import Config

# game = "Factorio"
# appID = SteamDBScraper.searchForTitle(game)

# for price in SteamDBScraper.getLowestPrices(appID, base="EUR"):
#     print(game + ": " + str(price.value) + str(price.currency) + " | " + "{:.2f}".format(float(price.cValue)) +
#           str(price.cCurrency))


ob = OfferBook.loadFromFile(Config.OfferBooking.FILES.getPriced(testing=True))

ob.print()

SteamDBScraper.setOfferBookAppIDs(ob)

with open("./cache/offer-book-priced-appided.json", "w") as f:
    f.write(ob.toJSON())

