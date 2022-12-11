
import math
import os.path

from ecolib.price import Price
from ecolib.threader import Threader
from ecolib.logger import lg as logging

from src.RedisCache import RedisCache
from src.dispatcher import Dispatcher
import json
import threading
from src.G2G.G2GOfferBook import OfferBook
from src.G2G.G2GOffer import Offer
from src.G2G.G2GFilterOffer import FilterOffer
from src.config import Config



with open(os.path.join(os.path.dirname(__file__), "price_filtering.json"), "r") as __file:
    FILTERING_CONFIGS = json.loads(__file.read())



BASE = Config.ExRates.BASE


class G2GScraper:

    @staticmethod
    def updateModuleConfigs():
        with open(os.path.join(os.path.dirname(__file__), "price_filtering.json"), "r") as _file:
            global FILTERING_CONFIGS
            FILTERING_CONFIGS = json.loads(_file.read())

    @staticmethod
    def _getBrandsOffers(brands):
        QUERY_SIZE = Config.G2G.BrandOffering.QUERY_SIZE
        INSTANCES = Config.G2G.BrandOffering.INSTANCES
        brandOffer = {}
        stringified_brands = []

        string_in_cause = ""
        idx = -1
        for b in range(0, len(brands)):
            idx = math.floor(b / 100)  # Porque é que isto divide por 100? Esqueci... faz tipo 30 dias desde que escrevi
            if b % QUERY_SIZE == 0 and b != 0:
                stringified_brands.append(string_in_cause[0:len(string_in_cause) - 1])
                string_in_cause = ""
            string_in_cause = string_in_cause + brands[b] + ","

        if len(brands) / QUERY_SIZE > idx:
            # print("Tem mais doq e divisivel por " + str(QUERY_SIZE))
            stringified_brands.append(string_in_cause[0:len(string_in_cause) - 1])
        else:
            stringified_brands[-1] = stringified_brands[-1][0:len(stringified_brands[-1]) - 1]

        js = []
        thread_pool = []

        def dispatchBranding(stringified_brand):
            # print(" A mandar a string:\n " + stringified_brand)
            res = Dispatcher.G2G_getBrandsOffer(stringified_brand)
            js.append(json.loads(res.content))


        for stringified_brand in stringified_brands:
            # print(stringified_brand)
            thread_pool.append(threading.Thread(target=dispatchBranding, args=(str(stringified_brand),)))



        T = Threader(lambda: thread_pool, INSTANCES)
        T.dispatch(endFunc=lambda s, e: print("Dispatched Branding Threads: [" + str(s) + "->" + str(e) + " <" +
                                      str(len(thread_pool)) + ">]"))

        try:
            for johnson in js:
                for bid in list(johnson["payload"].keys()):
                    brandOffer[str(bid)] = johnson["payload"][str(bid)]["total_result"]

        except KeyError as ke:
            return -1

        return brandOffer

    @staticmethod
    def _downloadRawCategories():
        categories = Dispatcher.G2G_getCategories()
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)),"cache/categories.json"), "w") as file:
            file.write(json.dumps(categories))

    @staticmethod
    def updateAccountCache():
        G2GScraper._downloadRawCategories()
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)),"cache/categories.json"), "r") as file:
            categories = json.loads(file.read())

        usefulHolders = {}
        kys = list(categories.keys())
        for i in range(0, len(kys)):
            # print("Passar pelo #" + str(i))
            if str(kys[i]).__contains__("-account"):
                # print("Achou : " + str(kys[i]))
                catHolder = categories[str(kys[i])]
                usefulHolders[str(kys[i])] = catHolder

        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)),"cache/accounts-unfiltered.json"), "w") as file:
            file.write(json.dumps(usefulHolders))

    @staticmethod
    def getOffers(testing=False) -> OfferBook:
        file = "accounts-unfiltered.json"
        if testing:
            file = "accounts-unfiltered-test-version.json"

        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)),"cache/" + file), "r") as file:
            accs_un = json.loads(file.read())
        k_accs_un = list(accs_un.keys())

        accs_offers = {}

        for k in range(0, len(k_accs_un) - 1):
            if "marketing_title" in accs_un[k_accs_un[k]]:
                accs_offers[str(accs_un[k_accs_un[k]]["marketing_title"]["zh-CN"])] = \
                    {
                        "path": str(k_accs_un[k]),
                        "brand": str(accs_un[k_accs_un[k]]["brand_id"])
                    }
        allBrands = []

        titles_to_check_black_list = []
        for acc_offer_title in list(accs_offers.keys()):
            titles_to_check_black_list.append(acc_offer_title)
        black_list = RedisCache.areBlackList(titles_to_check_black_list)

        for t, bl in black_list.items():
            if bl:
                accs_offers.pop(t)
                print("Popping Blacklist: " + str(t))

        for kao in list(accs_offers.keys()):
            allBrands.append(accs_offers[kao]["brand"])

        brandOffers = G2GScraper._getBrandsOffers(allBrands)  # adicionar property offers na brands

        goodOffers = []

        num = 0
        for k in list(accs_offers.keys()):
            acc = accs_offers[k]
            if "path" in acc and "brand" in acc:
                if acc["brand"] in brandOffers:
                    goodOffers.append(Offer(k, acc["path"], acc["brand"], count=brandOffers[acc["brand"]]))

                else:
                    print("Sem offers para o " + str(acc["brand"]))
                    num += 1
            else:
                num += 1
        print(str(num) + " Ofertas nao tinham algum parametro.")
        ob = OfferBook(goodOffers, sortType=-1, sortDir=-1)
        ob.updateOfferChanges("G2G", "Main acquire.", len(goodOffers))
        return ob

    @staticmethod
    def __G2G_filterPrices(offers):

        validOffers = []
        for o in offers:
            filteredOffer = FilterOffer(o,
                                        FILTERING_CONFIGS["title_keywords_whitelist"],
                                        FILTERING_CONFIGS["description_keywords_whitelist"],
                                        FILTERING_CONFIGS["title_keywords_blacklist"],
                                        FILTERING_CONFIGS["description_keywords_blacklist"],
                                        FILTERING_CONFIGS["extreme_blacklist"],
                                        FILTERING_CONFIGS["extreme_whitelist"]).performFiltering()
            if filteredOffer:
                validOffers.append(filteredOffer)
        validOffers.sort(key=lambda e: e.price)

        try:

            return {validOffers[0].offer["brand_id"]: validOffers[0].price}

        except (KeyError, IndexError):

            try:
                titleErrored = str(offers[0]["title"])
            except (KeyError, IndexError):
                return {}

            logging.warning("Offer cuja filtragem não conseguiu retornar nenhum preço minimo decente " +
                            titleErrored)
            return {}

    @staticmethod
    def setOfferBookLowestPrice(offerbook: OfferBook, maxQuerySize) -> None:
        thread_pool = []
        init_len = len(offerbook.offers)
        valid_offers = {}
        INSTANCES = Config.G2G.Offering.INSTANCES

        def _dispatchGetAndFilter(brand):
            r = Dispatcher.G2G_getLowestPrices(brand, maxQuerySize)
            try:
                if int(r["code"]) == 2000:
                    valid_offers.update(G2GScraper.__G2G_filterPrices(r["payload"]["results"]))
                else:
                    return
            except KeyError as ke:
                logging.error("Não pode dar retrieve nas Offers duma certa conta... (Provavelmente muito rápido?)")



        for offer in offerbook.offers:
            thread_pool.append(threading.Thread(target=_dispatchGetAndFilter, args=(offer.brand,)))

        tc = 0
        t = Threader(lambda: thread_pool, INSTANCES)

        t.dispatch(endFunc=lambda s, e: print("Dispatched Pricing: [" + str(s) + "->" + str(e) + " <" + str(len(thread_pool)) +
                                      ">]"))


        for vOfferBrand in valid_offers.keys():
            i = offerbook.getOfferIdxByBrandId(vOfferBrand)
            offerbook.offers[i].setG2GPrice(Price(valid_offers[vOfferBrand], BASE))
        offerbook.updateOfferChanges("G2G", "Remove offers without recognizable G2GPrice/weirdo pack.",
                                     -1 * (init_len-len(valid_offers)))
        offerbook.addFlag(OfferBook.Flags.G2G_PRICED)
        # valid_offers.sort(key=lambda e: e["display_price"]) isto n vale a pena pq é de jogos != aqui na zona
