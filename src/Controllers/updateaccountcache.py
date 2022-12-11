from threading import Thread

from . import BasicController
from ..G2G.G2GScraper import G2GScraper


class UpdateAccountCache(BasicController.BasicController):
    from src.routing import Router
    @staticmethod
    def POST(R: Router, jbody: dict = None):
        success, ob = R.RH.G2GData.tryRetrieveOfferbook()
        if not success:
            R.G2GDataLocked()
            return

        R.actionSucceeded("Branding Scan started...")
        R.RH.G2GData.lock("Scanning new Brands...")
        def detach():
            try:
                G2GScraper.updateAccountCache()
            finally:
                R.RH.G2GData.unlock()

        Thread(target=detach, daemon=True).start()

        # return

