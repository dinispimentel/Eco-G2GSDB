from threading import Thread
from typing import Tuple, List

from . import BasicController
from ..G2G.G2GScraper import G2GScraper
from ..config import Config


class Branding(BasicController.BasicController):
    from src.routing import Router

    @staticmethod
    def __areAllParamsValid(jbody: dict):
        bad_params: List[Tuple[str, str]] = []
        for k,v in jbody.items():
            if str(k) == "min_offers":
                try:
                    if int(v) < Config.G2G.BrandOffering.STATIC_MIN_OFFER_COUNT:
                        bad_params.append((str(k), f'Machine refuses to scrap categories with less than '
                                               f'{Config.G2G.BrandOffering.STATIC_MIN_OFFER_COUNT} offers.'))
                except (BaseException, Exception):
                    bad_params.append((str(k), "must be an integer."))
        return len(bad_params) < 1, bad_params



    @staticmethod
    def POST(R: Router, jbody: dict = None):
        success, ob = R.RH.G2GData.tryRetrieveOfferbook()
        if not success:
            R.G2GDataLocked()
            return

        allValid, bad_params = Branding.__areAllParamsValid(jbody)

        if not allValid:
            R.badParams(bad_params)
            return
        R.actionSucceeded("Branding started...")
        R.RH.G2GData.lock("G2G Branding...")
        def detach():
            try:
                new_ob = G2GScraper.getOffers()
                new_ob.removeCountBelowX(jbody.get('min_offers') or Config.G2G.BrandOffering.STATIC_MIN_OFFER_COUNT)
                R.RH.G2GData.offerbook = new_ob
            finally:
                R.RH.G2GData.unlock()

        Thread(target=detach, daemon=True).start()

        # return

