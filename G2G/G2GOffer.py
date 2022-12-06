import json




from config import Config
from typing import List

from ecolib.price import Price
from ecolib.logger import lg as logging












class Offer:
    KLASS = "Offer"

    def __init__(self, title, path, brand, count=None, steamprices=None, g2gprice=None, appID=None):
        self.steamprices: List[Price] = steamprices
        self.appID = appID
        self.g2gprice: Price = g2gprice
        self.count = count

        self.title = title
        self.path = path
        self.brand = brand

    def setOfferCount(self, c):
        self.count = c

    def setG2GPrice(self, gp: Price):
        self.g2gprice = gp

    def setAppID(self, appID):
        self.appID = appID

    def setSteamPrices(self, prices: List[Price]):
        self.steamprices = prices

    def getLowestSteamPrices(self) -> float:
        steam_lowest_price = 2**30
        if self.steamprices:
            for p in self.steamprices:
                if p.cValue:
                    if p.cValue < steam_lowest_price:
                        steam_lowest_price = p.cValue

        if steam_lowest_price != 2**30:
            return steam_lowest_price

    def isThereInvalidSteamPrices(self):

        for sp in self.steamprices:
            if sp.cValue is not None and sp.cValue != 0:
                return False
        return True

    def getSteamLowestPriceCurrency(self):
        steam_lowest_price = 2**30
        cur = None
        if self.steamprices:
            for p in self.steamprices:
                if p.cValue:
                    if p.cValue < steam_lowest_price:
                        steam_lowest_price = p.cValue
                        cur = p.currency
        return cur

    def print(self):
        lsp = self.getLowestSteamPrices()
        p = ((float(int((self.g2gprice.value - lsp) * 100) / 100)) / lsp) * 100
        pcur = self.getSteamLowestPriceCurrency()
        print(f"""################################
Title: {self.title}
Offers: {self.count}
G2GPrice: {float(int(self.g2gprice.value*100)/100)}{self.g2gprice.currency}
SteamPrice [lowest]: {float(int(self.getLowestSteamPrices()*100)/100)}{Config.ExRates.BASE} ({pcur})
Price difference: {float(int( (self.g2gprice.value - self.getLowestSteamPrices())*100 )/100)}{Config.ExRates.BASE}""" +
              f""" ({"↑" if p > 0 else "↓"} {float(int(p*100)/100)}%)
################################""")

    def toJSON(self):
        d = dict()

        d[str(self.title)] = {
            "brand": self.brand,
            "path": self.path,
            "count": self.count,
            "g2gprice": self.g2gprice.toJSON(),
            "steamprices": Price.jsonfyList(self.steamprices),
            "appID": self.appID
        }
        return json.dumps(d)

    def _dictify(self):

        d = dict()
        d[str(self.title)] = {
            "brand": self.brand,
            "path": self.path,
            "count": self.count,
            "g2gprice": self.g2gprice.toDICT(),
            "steamprices": Price.dictifyInnerList(self.steamprices),
            "appID": self.appID
        }
        return d

    @staticmethod
    def dictifyList(offers):
        d = dict()
        d["klass"] = "Offers"
        for offer in offers:
            d = {**d, **offer._dictify()}  # O que ja tinha merged com o outro
        return d

    @staticmethod
    def rebuildOffers(offers: dict):
        ofs = []
        if offers["klass"] != "Offers":
            logging.warning("Tentado reconstruir objeto como Offers sem a Klass Offers...")
            return
        offers.pop("klass")

        for key in list(offers.keys()):
            ofs.append(Offer(key,
                             offers[key]["path"],
                             offers[key]["brand"],
                             offers[key]["count"],
                             Price.reClassPrices(offers[key]["steamprices"]),
                             Price.reClassPrice(offers[key]["g2gprice"]),
                             offers[key]["appID"]
                             ))
        return ofs



