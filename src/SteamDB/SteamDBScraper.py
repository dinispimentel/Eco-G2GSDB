import json

import time
from difflib import SequenceMatcher
from threading import Thread
from typing import Callable

from src.G2G.G2GOfferBook import OfferBook, Exceptions
from src.RedisCache import RedisCache
from src.config import Config
from src.dispatcher import Dispatcher


from ecolib.price import Price
from ecolib.logger import lg as logging
from ecolib.threader import Threader
from ecolib.utils import Utils

countries = Config.SteamDB.AppPricing.COUNTRIES


BASE = Config.ExRates.BASE


class SteamDBScraper:

    # MOVIDO PARA CLASSE GLOBAL AO PROJETO

    # class Price:
    #
    #     def __init__(self, amount, currency, camount, ccurrency):
    #         self.amount = amount
    #         self.currency = currency
    #         self.convertedAmount = camount
    #         self.convertedCurrency = ccurrency

    @staticmethod
    def _updateInternalPriceConversion(currencies, base=None):
        form_cur = ""
        for cur in currencies:
            form_cur = form_cur + (base or BASE) + cur + ","

        response = Dispatcher.FxMarket_getForexQuotes(form_cur)

        res = json.loads(response.content)
        return res["price"]

    @staticmethod
    def searchForTitle(title):
        response = Dispatcher.SteamDB_GetAppIDFromTitle(title)
        res = json.loads(response.content)
        if len(res["hits"]) < 1:
            return None

        for h in res["hits"]:
            s = SequenceMatcher(None, h["name"], title)
            if s.ratio() > 0.70:
                return h["objectID"]

        return None

    @staticmethod
    def getLowestPrices(appIDs: str, triggerToSuspendAll, base=None, retries=0):

        prices = {}
        symbols = []



        for x in range(0, len(countries)):
            response = Dispatcher.Steam_GetAppIDPrice(appIDs, countries[x])
            if response.content is not None and response.content != "null" and response.content != "":

                if str(response.content).__contains__("Access Denied") or response.status_code != 200:
                    print(f'FORBIDDEN S_API: ' +
                          f'{Config.SteamDB.AppPricing.FORBIDDEN_TIMEOUT} secs wait')
                    triggerToSuspendAll(Config.SteamDB.AppPricing.FORBIDDEN_TIMEOUT)
                    time.sleep(Config.SteamDB.AppPricing.FORBIDDEN_TIMEOUT)
                    if retries < 3:
                        return SteamDBScraper.getLowestPrices(appIDs, triggerToSuspendAll, base=base, retries=retries + 1)
                    else:
                        return None

                else:
                    # print(response.content)
                    res = json.loads(response.content)
                    for aID in Utils.dismountStringifiedArray(appIDs):
                        if (res is not None) and res[str(aID)]:
                            try:
                                if res[str(aID)]["success"] != "false":


                                    if "price_overview" in res[str(aID)]["data"]:
                                        pov = res[str(aID)]["data"]["price_overview"]
                                        newPrice = Price(
                                            float(pov["final"]) / 100, pov["currency"],
                                            cValue=-1,
                                            cCurrency=base or BASE
                                        )
                                        if str(aID) in list(prices.keys()):
                                            PList = prices.get(str(aID))
                                            PList.append(newPrice)
                                            prices.update(
                                                {
                                                    str(aID): PList
                                                }
                                            )
                                        else:
                                            prices.update({str(aID): [newPrice]})

                                else:
                                    return None
                            except KeyError as KE:
                                pass

        # for p in prices.values():
        #     symbols.append(p.currency)  # TODO: Supostamente isto passaria para o ExRates para ver se suporta todos



        # FUTURO (QUANDO TIVER A RODAR EM PRODUCTION)
        # MOVER ISTO PARA UMA CHAMADA DE 5 mins de INTERVALO
        # ALTERNATIVA OPTADA -> PEDIR AO SERVER DE EXRATES

        exrates_base = Dispatcher.ExRates_getBase()
        if (base or BASE) != exrates_base:
            Dispatcher.ExRates_forceUpdate(base=(base or BASE), currencies=Config.SteamDB.AppPricing.EXRATES_COUNTRIES_CURRENCIES)
        # exrates = SteamDBScraper._updateInternalPriceConversion(symbols, base=base)
        exrates = Dispatcher.ExRates_getRates()

        for pList in prices.values():
            for p in pList:
                try:
                    if p.currency == (base or BASE):
                        p.cValue = p.value
                    else:
                        p.cValue = round(float(p.value) / float(exrates[(base or BASE) + str(p.currency)]), 3)
                except KeyError:
                    logging.error("Não foi possível converter: " + str(p.currency) + "->" + str(p.cCurrency))

        return prices

    @staticmethod
    def retrieveAppIDs(offerbook: OfferBook) -> None:
        thread_pool = []

        def __dispatchAppIDs(title: str, tosave_appid_redis: Callable[[str, int], None]):
            appID = SteamDBScraper.searchForTitle(title)
            if not appID:
                logging.warning("Não foi encontrado o AppID de: " + title)
            else:
                offer_idx = offerbook.getOfferIdxByTitle(title)
                offerbook.offers[offer_idx].setAppID(appID)
                tosave_appid_redis(title, appID)

        titles = []

        for offer in offerbook.offers:
            titles.append(offer.title)
        appIds = RedisCache.getAppIDs(titles)
        titles_to_scrap = []

        for i in range(len(titles)):
            if appIds[i] is not None:
                offer_idx = offerbook.getOfferIdxByTitle(titles[i])
                offerbook.offers[offer_idx].setAppID(appIds[i].decode("utf-8"))
            else:
                titles_to_scrap.append(titles[i])

        toSave = {}
        def annotate_to_save(title: str, appId: int):
            toSave.update({title: appId})

        for title_to_scrap in titles_to_scrap:
            thread_pool.append(Thread(target=__dispatchAppIDs, args=(title_to_scrap, annotate_to_save)))

        T = Threader(lambda: thread_pool, Config.SteamDB.AppIDing.INSTANCES)
        T.dispatch(endFunc=lambda s, e: print(f'Dispatched AppIDing: [{s}->{e} <{len(offerbook.offers)}>]'))
        RedisCache.saveAppIDs(toSave)
        offerbook.addFlag(OfferBook.Flags.STEAM_APPIDED)


    @staticmethod
    def retrieveSteamPrices(offerbook: OfferBook, base: str) -> None:
        cf, fnf = offerbook.containsFlags([OfferBook.Flags.STEAM_APPIDED, OfferBook.Flags.STEAM_APPID_SANITIZED])
        if not cf:
            raise Exceptions.OfferBookMissingFlag(f'Need to sanitize the Steam AppIDs\n Flags missing:'
                                                  f'{OfferBook.Flags.convertFlagNumbersToStrs(fnf)}')

        thread_pool = []
        querying_app_ids = Utils.mountQuerysStringifiedArrays(offerbook.getAllAppIds(),
                                                              Config.SteamDB.AppPricing.QUERY_SIZE)

        def __dispatchSteamPricing(appIDs: str):
            prices = SteamDBScraper.getLowestPrices(appIDs, T.suspendAllForXTime, base=base)

            for aID, priceList in prices.items():

                offer_idx = offerbook.getOfferIdxByAppID(aID)
                offerbook.offers[offer_idx].setSteamPrices(priceList)


        for QAIDs in querying_app_ids:

            thread_pool.append(Thread(target=__dispatchSteamPricing, args=(QAIDs,)))

        T = Threader(lambda: thread_pool, Config.SteamDB.AppPricing.INSTANCES,
                     delay_config=Config.SteamDB.AppPricing.DELAY_CONFIG)

        T.dispatch(endFunc=lambda s, e: print(f'Dispatched AppIDPricing: [{s}->{e} <{len(querying_app_ids)}>]'))
        offerbook.addFlag(OfferBook.Flags.STEAM_PRICED)