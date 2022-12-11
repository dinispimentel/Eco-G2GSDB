from threading import Thread
from typing import List, Tuple

from . import BasicController

from ..G2G.G2GScraper import G2GScraper
from ..config import Config


class Pricing(BasicController.BasicController):
    from src.routing import Router

    @staticmethod
    def __areAllParamsValid(jbody: dict):
        bad_params: List[Tuple[str, str]] = []
        for k, v in jbody.items():
            if str(k) == "currency":
                if str(v) not in Config.G2G.Pricing.ALLOWED_CURRENCIES:
                    bad_params.append((str(k), f'{v} not in {Config.G2G.Pricing.ALLOWED_CURRENCIES}'))
        return len(bad_params) < 1, bad_params
    @staticmethod
    def POST(R: Router, jbody: dict = None):
        success, ob = R.RH.G2GData.tryRetrieveOfferbook()
        if not success:
            R.G2GDataLocked()
            return

        allValid, bp = Pricing.__areAllParamsValid(jbody)
        if not allValid:
            R.badParams(bp)
            return

        allf, fm = ob.containsFlags([ob.Flags.G2G_BRANDED])
        if not allf:
            R.OfferBookMissingFlags(fm)
            return

        R.actionSucceeded("Pricing started...")
        R.RH.G2GData.lock("G2G Pricing...")
        def detach():
            try:
                G2GScraper.retrieveLowestPrices(ob, Config.G2G.Pricing.MAX_QUERY, currency=jbody.get('currency') or
                                                                                           'USD')
                ob.removeOffersWithoutG2GPrice()
            finally:
                R.RH.G2GData.unlock()

        Thread(target=detach, daemon=True).start()

        # return
