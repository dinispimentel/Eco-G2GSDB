import copy
import json
from typing import List, Tuple, Type

from ecolib.serverutils import ServerUtils
from ecolib.utils import Utils

from .DPHTTPRequestHandler import DPHTTPRequestHandler


from .DPHTTPRequestHandler import DPHTTPRequestHandler, ERRORS, SUCCESSES
from .G2G.G2GOfferBook import OfferBook


# from .Models.DMOfferBook import OfferBook


class Router:
    GetRoutes = {
        "STATUS": "/status",
        "LATEST_UPDATE_G2G_DATA_WHEN": "/lastUpdateG2GData",
        "RETRIEVE_BEST_DEALS": "/bestdeals"
    }

    PostRoutes = {
        "CHECK_G2G_NEW_BRANDS" : "/check-new-brands",
        "BRAND": "/brand-it",
        "PRICE": "/g2g-price-it",
        "STEAM_APP_ID": "/steam-app-id-it",
        "STEAM_PRICE": "/steam-price-it"
    }

    PatchRoutes = {
        "CONVERT_CURRENCY" : "/convertOfferBookCur"
    }

    def __init__(self, RH: DPHTTPRequestHandler):
        self.RH: DPHTTPRequestHandler = RH

    def __dealWithContentLength(self):
        if not self.RH.headers.get('Content-Length'):
            return 0
        content_len = int(self.RH.headers.get('Content-Length'))
        if not content_len or (2 ** 31) - 1 > int(content_len) < 0:
            # self.write_response("<html>Bad request</html>", code=400, content_type="text/html")
            return 0
        else:
            return content_len


    def GET(self):
        content_len = Router.__dealWithContentLength(self)
        path = self.RH.path
        jbody = None
        if content_len > 0:
            jbody = json.loads(self.RH.rfile.read(content_len))

        if path == self.GetRoutes["STATUS"]:
            from .Controllers.status import Status
            Status.GET(self)
        # elif path == self.GetRoutes["LATEST_UPDATE_DMARKET_DATA_WHEN"]:
        #     from .Controllers.latestdmarketdata import LatestDMarketData
        #     LatestDMarketData.GET(self)
        elif path == self.GetRoutes["RETRIEVE_BEST_DEALS"]:
            from .Controllers.retrievebestdeals import RetrieveBestDeals
            # JBODY: {sort_type: int, sort_direction: int, offer_limit: int}
            RetrieveBestDeals.GET(self, jbody=jbody)

    def POST(self):
        content_len = self.__dealWithContentLength()
        # if not content_len:
        #     self.write_response(json.dumps({"success": False, "msg": "Please provide Header Content-Length."}),
        #                         code=400)
        #     return
        path = self.RH.path
        jbody = None
        if content_len > 0:
            jbody = json.loads(self.RH.rfile.read(content_len))

        if path == self.PostRoutes["CHECK_G2G_NEW_BRANDS"]:
            from .Controllers.updateaccountcache import UpdateAccountCache
            UpdateAccountCache.POST(self, jbody={})
        elif path == self.PostRoutes["BRAND"]:
            from .Controllers.branding import Branding
            Branding.POST(self, jbody=jbody)
        elif path == self.PostRoutes["PRICE"]:
            from .Controllers.pricing import Pricing
            Pricing.POST(self, jbody=jbody)
        elif path == self.PostRoutes["STEAM_APP_ID"]:
            from .Controllers.appiding import AppIDing
            AppIDing.POST(self, jbody={})
        elif path == self.PostRoutes["STEAM_PRICE"]:
            from .Controllers.steampricing import SteamPricing
            SteamPricing.POST(self, jbody=jbody)

    # def PATCH(self):
    #     path = self.RH.path
    #     content_len = self.__dealWithContentLength()
    #     jbody = None
    #     if content_len > 0:
    #         jbody = json.loads(self.RH.rfile.read(content_len))
    #     if path == self.PatchRoutes["CONVERT_CURRENCY"]:
    #         from .Controllers.convertcurrency import ConvertCurrency
    #         ConvertCurrency.PATCH(self, jbody=jbody)

    def missingParams(self, missingParams: list):
        er = copy.deepcopy(ERRORS["null_json"])
        er.update({'msg': er['msg'] + f'\n{missingParams}'})
        self.write_response(json.dumps(er), code=400)

    def badParamsTypes(self, bad_params_tuple_list: List[Tuple[str, Type, List[Type]]]):
        """

        :param bad_params_tuple_list: [(Key, Wrong Type, [Good Types])]
        :return:
        """
        er = copy.deepcopy(ERRORS["bad_params"])
        msg = er['msg']
        for t in bad_params_tuple_list:
            msg += f'\n {t[0]}: {t[1].__name__} doesn\'t match any of supported types: ' \
                   f'{[ty.__name__ for ty in t[2]]}'

        er.update({"msg": msg})
        self.write_response(json.dumps(er), code=400)

    def badParams(self, bad_params_tuple_list: List[Tuple[str, str]]):
        er = copy.deepcopy(ERRORS["bad_params"])
        msg = er['msg']
        for t in bad_params_tuple_list:
            msg += "\n" + t[0] + ": " + t[1]

        er.update({"msg": msg})
        self.write_response(json.dumps(er), code=400)

    def actionSucceeded(self, content: str = None):
        sc = copy.deepcopy(SUCCESSES["action_succeded"])
        sc.update({"msg": sc["msg"] + " " + (str(content) if content else "")})
        self.write_response(json.dumps(sc))

    def G2GDataLocked(self, extra=""):
        er = copy.deepcopy(ERRORS['data_locked'])
        er.update({"msg": er["msg"] + f'\n{extra}'})
        self.write_response(json.dumps(er), code=400)

    def OfferBookMissingFlags(self, flags_missing: List[int]):
        er = copy.deepcopy(ERRORS['offer_book_missing_flag'])
        er.update({"msg": er["msg"] + f'\n{OfferBook.Flags.convertFlagNumbersToStrs(flags_missing)}'})
        self.write_response(json.dumps(er), code=400)

    def OfferNeedsPriceConversion(self, dm_cur: str, sm_cur: str):
        er = copy.deepcopy(ERRORS['offer_book_currency_mismatch'])
        er.update({"msg": er["msg"] + f'{dm_cur}(DM) -> {sm_cur}(SM)'})
        self.write_response(json.dumps(er), code=400)

    def retrieveOfferBook(self, ob: OfferBook):
        jres = {"success": True, "offerbook": ob.toDICT()}
        self.write_response(json.dumps(jres))

    def InternalError(self, extra=""):
        er = copy.deepcopy(ERRORS['internal_error'])
        er.update({"msg": er["msg"] + f'\n{extra}'})
        self.write_response(json.dumps(er), code=500)

    def write_response(self, content: str, **kwargs):
        """
        Escreve um corpo de resposta na Response, com código de resposta e headers.
        :param content: str
        :param kwargs: code: int, content_type: str,
                      extra_headers: List[Tuple[str, str]]
        :return:
        """
        return ServerUtils.writeResponse(self.RH, content, **kwargs)
