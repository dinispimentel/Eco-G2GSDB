from threading import Thread

from . import BasicController
from ..G2G.G2GOfferBook import OfferBook

from ..G2G.G2GScraper import G2GScraper
from ..SteamDB.SteamDBScraper import SteamDBScraper
from ..config import Config


class AppIDing(BasicController.BasicController):
    from src.routing import Router

    @staticmethod
    def POST(R: Router, jbody: dict = None):
        success, ob = R.RH.G2GData.tryRetrieveOfferbook()
        if not success:
            R.G2GDataLocked()
            return

        allf, fm = ob.containsFlags([ob.Flags.G2G_PRICED, ob.Flags.G2G_PRICE_SANITIZED])
        if not allf:
            R.OfferBookMissingFlags(fm)
            return

        R.actionSucceeded("Steam App-IDing started...")
        R.RH.G2GData.lock("Steam App-IDing...")
        def detach():
            try:
                SteamDBScraper.retrieveAppIDs(ob)
                ob.removeOffersWithoutAppID()
            finally:
                R.RH.G2GData.unlock()

        Thread(target=detach, daemon=True).start()

        # return
