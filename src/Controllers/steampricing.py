from __future__ import annotations

from threading import Thread
from typing import Tuple, List, Type, Dict

from . import BasicController
from ..G2G.G2GOfferBook import OfferBook

from ..G2G.G2GScraper import G2GScraper
from ..SteamDB.SteamDBScraper import SteamDBScraper
from ..config import Config


class SteamPricing(BasicController.BasicController):
    from src.routing import Router

    @staticmethod
    def __areAllParamsValid(req_kv: dict):
        bad_params: List[Tuple[str, str]] = []
        for k, v in req_kv.items():

            if str(k) == "base_currency":
                if v not in Config.ExRates.ALLOWED_CURRENCIES:
                    bad_params.append((str(k), f'not in {Config.ExRates.ALLOWED_CURRENCIES}'))
        return len(bad_params) < 1, bad_params





    @staticmethod
    def POST(R: Router, jbody: dict = None):
        success, ob = R.RH.G2GData.tryRetrieveOfferbook()
        if not success:
            R.G2GDataLocked()
            return

        mp = SteamPricing.check_params_missing(jbody)
        if len(mp) > 0:
            R.missingParams(mp)
            return
        err_supp = SteamPricing.check_param_type(jbody)
        if len(err_supp) > 0:
            R.badParamsTypes(err_supp)
            return

        allValid, bp = SteamPricing.__areAllParamsValid(jbody)
        if not allValid:
            R.badParams(bp)
            return

        allf, fm = ob.containsFlags([ob.Flags.STEAM_APPIDED, ob.Flags.STEAM_APPID_SANITIZED])
        if not allf:
            R.OfferBookMissingFlags(fm)
            return

        R.actionSucceeded("Steam Pricing started...")
        R.RH.G2GData.lock("Steam Pricing...")

        def detach():
            try:
                SteamDBScraper.retrieveSteamPrices(ob, jbody.get("base_currency"))
                ob.removeOffersWithoutAnySteamPrice()
            finally:
                R.RH.G2GData.unlock()

        Thread(target=detach, daemon=True).start()

        # return
    @staticmethod
    def getRequiredParams() -> Dict[str, Type | Tuple]:
        return {
            "base_currency": str
        }
