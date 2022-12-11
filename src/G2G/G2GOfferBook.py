from __future__ import annotations

import json
from src.G2G.G2GOffer import Offer
from typing import List, Tuple


# from aenum import Enum, skip



class NumOff:

    def __init__(self, rem):
        self.rem = 0

    def increment(self):
        self.rem += 1

    def get(self):
        return self.rem

class SORTING:


    class OPTIONS:


        class FUNCS:
            @staticmethod
            def offerOrder(e):
                return e.count

            @staticmethod
            def abcOrder(e):
                return e.title

            @staticmethod
            def brandOrder(e):
                return e.brand

            @staticmethod
            def priceGapOrder(e: Offer):
                lsp = e.getLowestSteamPrices()
                if lsp and e.g2gprice.value:
                    return e.g2gprice.value - lsp
                else:
                    return 2**32

            @staticmethod
            def priceGapPercentage(e: Offer):
                lsp = e.getLowestSteamPrices()
                if lsp and e.g2gprice.value:
                    return ((lsp - e.g2gprice.value) / lsp) * 100
                else:
                    return 2**32

        @staticmethod
        def FUNC_TO_NAME(f):
            try:
                if f == SORTING.OPTIONS.FUNCS.offerOrder:
                    return "Offers"
                elif f == SORTING.OPTIONS.FUNCS.abcOrder:
                    return "Alphabetic"
                elif f == SORTING.OPTIONS.FUNCS.brandOrder:
                    return "BrandId"
                else:
                    return "unsorted"
            except TypeError as te:
                return "unsorted"


    class DIRECTION:
        ASCENDANT = 0
        DESCENDANT = 1


class Exceptions:

    class OfferBookMissingFlag(Exception):
        pass


class OfferBook:
    class Flags:
        G2G_PRICED = 0
        G2G_PRICE_SANITIZED = 1
        STEAM_APPIDED = 2
        STEAM_APPID_SANITEZED = 3
        STEAM_PRICE_SANITIZED = 4
        STEAM_PRICED = 5


        @staticmethod
        def createConvDict():
            __convDict = dict(OfferBook.Flags.__dict__)
            __goodDict = {}
            for k, v in __convDict.items():
                if k[0] != "_" and type(v) == type(1):
                    __goodDict.update({str(v): k})
            return __goodDict

        @staticmethod
        def convertFlagNumbersToStrs(nums: List[int]):
            ss = []
            convDict = OfferBook.Flags.createConvDict()

            for num in nums:
                ss.append(convDict[str(num)])
            return ss





    KLASS = "OfferBook"
    # OBSOLETE

    # def _listifyOrders(self, offers):
    #     """
    #
    #     :param offers: Offer[]
    #     :return:
    #     """
    #     sOffers = []
    #     for offer in offers:
    #         offer_list.append([key, offer_dict[str(key)]])
    #     self.orders = offer_list

    def __init__(self, offers: List[Offer]=None, sortType=-1, sortDir=-1, offer_changes=None, flags=None):
        if flags is None:
            flags = []
        if offer_changes is None:
            offer_changes = []

        self.offers = offers or [] # Sorted Offers
        self.sortType = sortType
        self.sortDir = sortDir
        self.offer_changes: List[dict] = offer_changes
        self.flags: List[int] = flags
        # self._listifyOrders(offers)


    def sort(self, sort_type, sort_direction):

        rev = False
        if sort_direction == SORTING.DIRECTION.DESCENDANT:
            rev = True


        self.offers.sort(key=sort_type, reverse=rev)
        self.sortType = sort_type
        self.sortDir = "Normal" if not rev else "Reverse"

    def getOfferByIndex(self, idx):
        return self.offers[idx]

    def getOfferIdxByBrandId(self, brand):
        for i in range(len(self.offers)):
            if brand == self.offers[i].brand:
                return i
        return None

    def getOfferIdxByTitle(self, title):
        for i in range(len(self.offers)):
            if title == self.offers[i].title:
                return i
        return None

    def getOfferIdxByAppID(self, appID):
        for i in range(len(self.offers)):
            if appID == self.offers[i].appID:
                return i
        return None

    def getAllAppIds(self):
        aIs = []
        for offer in self.offers:
            aIs.append(offer.appID)
        return aIs


    def updateOfferChanges(self, side, phase, num):

        self.offer_changes.append({
            "Initiator": side,
            "Phase": phase,
            "Number": f'{"+" if num > 0 else ""}{num}'
        })


    def toJSON(self) -> str:
        d = dict()
        d["klass"] = OfferBook.KLASS
        d["offers"] = Offer.dictifyList(self.offers)
        d["sortType"] = SORTING.OPTIONS.FUNC_TO_NAME(self.sortType)
        d["sortDir"] = self.sortDir
        d["offerChanges"] = self.offer_changes
        d["flags"] = self.flags

        return json.dumps(d)

    @staticmethod
    def rebuild(j):

        d = json.loads(j)

        if d["klass"] != OfferBook.KLASS:
            raise Exception("Error ao reconstruir: classe errada")

        return OfferBook(Offer.rebuildOffers(d["offers"]), sortType=d["sortType"], sortDir=d["sortDir"], offer_changes=
                         d["offerChanges"], flags=d["flags"])

    @staticmethod
    def loadFromFile(fname):
        print(fname)
        with open(fname, "r") as file:
            ob_raw = file.read()
        ob = OfferBook.rebuild(ob_raw)
        return ob

    def writeToFile(self, fname):
        with open(fname, "w") as f:
            f.write(self.toJSON())


    def removeCountBelowX(self, x):
        init_len = len(self.offers)
        filtered_offers = []
        for offer in self.offers:
            if not offer.count < x:
                filtered_offers.append(offer)

        self.offers = filtered_offers
        self.updateOfferChanges("User", f"Remove count below {x}", -1 * (init_len - len(filtered_offers)))

    def countBrandsWithoutOffers(self):
        c = 0
        for offer in self.offers:
            if not offer.g2gprice or offer.g2gprice == 0:
                c += 1
        return c

    # [OBSOLETE]
    # Reconstruí sem querer isto na classe Offer e nem usava

    # @staticmethod
    # def __reClassifyOffers(offers: dict):
    #     new_offers = []
    #     try:
    #         if not (Offer.KLASS == offers["klass"]):
    #             raise Exception("Error ao reconstruir: classe errada")
    #         offers.pop(“klass“)
    #
    #         for key in list(offers.keys()):
    #             offer = offers[key]
    #             new_offers.append(
    #                 Offer(key, offer["path"], offer["brand"], offer["count"],)
    #             )
    #
    #     except KeyError:
    #         logging.error(“Erro ao reconstruir Offers.“)

    # [/OBSOLETE]

    def __removeOffersWithoutG2GPrice(self, incrementNumRemoved):

        for offer_idx in range(0, len(self.offers)):

            if not self.offers[offer_idx].g2gprice or self.offers[offer_idx].g2gprice is None:
                self.offers.pop(offer_idx)
                self.__removeOffersWithoutG2GPrice(incrementNumRemoved)
                incrementNumRemoved()

                return
        return

    def removeOffersWithoutG2GPrice(self):

        nf = NumOff(0)

        self.__removeOffersWithoutG2GPrice(nf.increment)
        self.updateOfferChanges("G2G", "Remove offers without G2G Price.", -1 * nf.get())
        self.addFlag(OfferBook.Flags.G2G_PRICE_SANITIZED)

    def __removeOffersWithoutAppID(self, incrementFunc):
        for offer_idx in range(0, len(self.offers)):
            if not self.offers[offer_idx].appID or self.offers[offer_idx].appID == -1:
                self.offers.pop(offer_idx)
                self.__removeOffersWithoutAppID(incrementFunc)
                return
        return

    def removeOffersWithoutAppID(self):
        nf = NumOff(0)

        self.__removeOffersWithoutAppID(nf.increment)
        self.updateOfferChanges("Steam", "Remove offers without AppID.", -1 * nf.get())
        self.addFlag(OfferBook.Flags.STEAM_APPID_SANITEZED)

    def __removeOffersWithoutAnySteamPrice(self, incrementFunc):
        for offer_idx in range(0, len(self.offers)):
            if (not self.offers[offer_idx].steamprices or len(self.offers[offer_idx].steamprices) < 1)\
                    or self.offers[offer_idx].isThereInvalidSteamPrices():
                self.offers.pop(offer_idx)
                self.__removeOffersWithoutAnySteamPrice(incrementFunc)
                return
        return

    def removeOffersWithoutAnySteamPrice(self):
        nf = NumOff(0)

        self.__removeOffersWithoutAnySteamPrice(nf.increment)
        self.updateOfferChanges("Steam", "Remove offers without Price.", -1 * nf.get())
        self.addFlag(OfferBook.Flags.STEAM_PRICE_SANITIZED)



    def print(self):
        print("Offers" + str(self.offers))
        print("Flags: " + str(OfferBook.Flags.convertFlagNumbersToStrs(self.flags)))
        print("NumOfOffers: " + str(len(self.offers)))
        print("Sort Order: " + str(SORTING.OPTIONS.FUNC_TO_NAME(self.sortType)))
        print("Sort Direction: " + str(self.sortDir))
        print("Offer changes: ")
        for oc in self.offer_changes:
            print(f'| {oc["Initiator"]} | : {oc["Phase"]} -> {oc["Number"]}')

    # def genSubOfferBook(self, configs=None):
    #     fob = self
    #     if configs is None:
    #         configs = {
    #             "minium-offer-count": 0
    #                    }
    #
    def addFlag(self, flag: int):

        if not (flag in self.flags):
            self.flags.append(flag)

    def containsFlags(self, flags: List[int]) -> Tuple[bool, List[int]]:
        flags_not_found = []
        for flag in flags:
            if not (flag in self.flags):
                flags_not_found.append(flag)

        return True if len(flags_not_found) < 1 else False, flags_not_found

    def printXOffers(self, x):
        if x > len(self.offers):
            x = len(self.offers) -1
        for i in range(0, x+1):
            self.offers[i].print()
