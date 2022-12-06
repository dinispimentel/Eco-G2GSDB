from G2G.G2GScraper import G2GScraper
from SteamDB.SteamDBScraper import SteamDBScraper
from G2G.G2GOfferBook import OfferBook, SORTING
from config import Config
# CategoriesHandler.selectAccountsFromCategories()
# with open("cache/accounts-unfiltered.json", "r") as file:
#     accs = json.loads(file.read())

# print(len(list(accs.keys())))


# def printAccs():
#    for x in list(accs.keys()):
#         print(x)

# game = "FIFA 22"
# appID = SteamDBScraper.searchForTitle(game)

# print(game + ": ")
# for p in SteamDBScraper.getLowestPrices(appID):
#     print(str(p.amount) + " " + str(p.currency) + " || "
#           + str(p.convertedAmount) + " " + str(p.convertedCurrency))

# print(G2GScraper._getBrandsOffers(["lgc_game_29302", "lgc_game_23618"]))

TESTING = False
BASE = Config.ExRates.BASE
# G2GScraper.updateAccountCache()
# ob = G2GScraper.getOffers(testing=TESTING)

# ob.removeCountBelowX(30)
# G2GScraper.setOfferBookLowestPrice(ob, 5)
# ob.removeOffersWithoutG2GPrice()
# ob.writeToFile(Config.OfferBooking.FILES.getPriced(testing=TESTING))
# ob = OfferBook.loadFromFile(Config.OfferBooking.FILES.getPriced(testing=TESTING))
# SteamDBScraper.setOfferBookAppIDs(ob)
# ob.removeOffersWithoutAppID()
# ob.writeToFile(Config.OfferBooking.FILES.getAppIDed(testing=TESTING))
# SteamDBScraper.setOfferBookSteamPrices(ob, BASE)
ob = OfferBook.loadFromFile(Config.OfferBooking.FILES.getSteamPriced(testing=TESTING))
# SteamDBScraper.setOfferBookSteamPrices(ob, BASE)
ob.print()
# ob = OfferBook.loadFromFile(Config.OfferBooking.FILES.getSteamPriced(testing=TESTING))
# ob.removeCountBelowX(40)
# ob = OfferBook.loadFromFile(Config.OfferBooking.FILES.getSteamPriced(testing=TESTING))
ob.removeOffersWithoutAnySteamPrice()
ob.removeCountBelowX(50)
ob.sort(SORTING.OPTIONS.FUNCS.priceGapPercentage, SORTING.DIRECTION.ASCENDANT)
ob.printXOffers(25)
# ob.printXOffers(50)


# ob.sort(SORTING.OPTIONS._FUNCS.offerOrder, SORTING.DIRECTION.DESCENDANT)
#
# ob.removeCountBelowX(1)
#
# with open("./cache/offers-ordered.json", "w") as file:
#     file.write(ob.jsonfy())
#
# G2GScraper.getOfferBookLowestPrice(ob, Config.G2G.Offering.QUERY_SIZE)
#
# print("Existem " + str(ob.countBrandsWithoutOffers()) + " brands sem preço mínimo G2G.")
#
# with open("./cache/offerbook-priced.json", "w") as file:
#     file.write(ob.jsonfy())





# game = "DayZ"
# appID = SteamDBScraper.searchForTitle(game)
# prices = SteamDBScraper.getLowestPrices(appID)
# print(appID)
#
# for price in prices:
#     print(price.getFxFmtString())

