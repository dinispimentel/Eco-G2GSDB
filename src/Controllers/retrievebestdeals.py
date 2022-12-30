from __future__ import annotations

from typing import List, Dict, Tuple, Type

from ecolib.utils import Utils

from src.Controllers.BasicController import BasicController
from src.G2G.G2GOfferBook import OfferBook, SORTING
from src.routing import Router


class RetrieveBestDeals(BasicController):

    @staticmethod
    def __areAllParamsValid(ps: Dict, offer_max_limit: int) -> Tuple[bool, List[Tuple[str, str]]]:
        params_invalid = []
        try:

            for k, v in ps.items():
                if str(k) == "sort_type":
                    convDict = SORTING.createConvDict()
                    try:
                        SORTING.convertNameToFunc(str(v))
                    except KeyError:
                        params_invalid.append((str(k),
                                               f'\n{str(v)} not in {[k for k in list(convDict.keys())]}'))

                if str(k) == "sort_direction":
                    if int(v) not in [0, 1]:
                        params_invalid.append((str(k),
                                               f'\n1 < {int(v)} < 0'))
                if str(k) == "offer_count":
                    if not (0 < int(v) <= offer_max_limit):
                        params_invalid.append((str(k),
                                              f'\n{offer_max_limit} < {int(v)} <= 0'))
                if str(k) == "offset":
                    if int(v) + int(ps.get('offer_count')) > offer_max_limit:
                        params_invalid.append((str(k),
                                               f'\n{int(v) + int(ps.get("offer_count"))} > {offer_max_limit}'))
        except (AttributeError, Exception):
            return False, params_invalid
        return len(params_invalid) < 1, params_invalid

    @staticmethod
    def GET(R: Router, **kwargs):
        t = R.RH.G2GData.tryRetrieveOfferbook()
        success = t[0]
        if success:
            ob: OfferBook = t[1]
            allf, fm = ob.containsFlags([ob.Flags.STEAM_PRICED])
            jbody: dict = kwargs.get("jbody")
            if not allf:
                R.OfferBookMissingFlags(fm)
                return
            mp = RetrieveBestDeals.check_params_missing(jbody)
            if len(mp) > 0:
                R.missingParams(mp)
                return
            err_supp = RetrieveBestDeals.check_param_type(jbody)
            if len(err_supp) > 0:
                R.badParamsTypes(err_supp)
                return



            # ESTA CONFIRMAÇÃO NÃO FAZ SENTIDO PORQUE: A STEAM TEM VÁRIOS PREÇOS, E, TODOS CONVERTIDOS PARA A
            # CURRENCY DA G2G
            # if (ob.offers[0].g2gprice.currency != ob.offers[0].steamprices[0].currency) and \
            #         ((ob.offers[0].g2gprice.cCurrency != ob.offers[0].steamprices[0].currency) or
            #          not ob.offers[0].g2gprice.cCurrency) and \
            #         ((ob.offers[0].g2gprice.currency != ob.offers[0].steamprices[0].currency) or
            #          not ob.offers[0].steamprices[0].currency) and \
            #         ((ob.offers[0].g2gprice.cCurrency != ob.offers[0].steamprices[0].currency) or
            #          (not ob.offers[0].g2gprice.cCurrency) or (not ob.offers[0].steamprices[0].currency)):
                # PROBLEMA: TRUE
                # NORMAL: FALSE
                # Esses boleanos complicados são para caso um seja None não aprovar/desaprovar por aí
                # Ex : G2GcCur (None) != SMcCur (None) -> False
                # Mas: (G2GcCur (None) != SMcCur (None) ) or (not G2GcCur) or (not SMcCur) <->
                # ---> (False or True or True) -> True
                # Tem and's em todas as clausulas
                # Deve ter problemas esta lógica, mas depois descobre-se

                # R.OfferNeedsPriceConversion(ob.offers[0].g2gprice.currency, ob.offers[0].steamprices[0].currency)
                # return
            params = RetrieveBestDeals.getRequiredOnlyKVPairs(jbody)
            allValid, params_invalid = RetrieveBestDeals.__areAllParamsValid(params, len(ob.offers))
            if not allValid:
                R.badParams(params_invalid)
                R.RH.G2GData.unlock()
                return
            try:  # Non-Detachable cz its fast and need to return the OfferBook '-'
                R.RH.G2GData.lock(status="Retrieving best deals")  # LOCK -> TODAS AS EXCPT: PRA BAIXO DEVEM DAR UNLOCK
                sortFunc = SORTING.convertNameToFunc(params.get('sort_type'))
                sortDir = int(params.get('sort_direction'))
                offer_count = int(params.get('offer_count'))
                offset = int(params.get('offset')) or 0
                ob.sort(sortFunc, sortDir)
                sob = ob.getSubsetOfferBook(offer_limit=offer_count, offset=offset)
                sob.sort(sortFunc, sortDir)
                # ob.writeToFile("/home/dp/Desktop/Eco-G2GSDB/src/cache/myofferbook.json") # TEST
                R.RH.G2GData.unlock()
                R.retrieveOfferBook(sob)
            except (Exception, BaseException):
                R.RH.G2GData.unlock()
        else:
            R.G2GDataLocked()



    @staticmethod
    def POST(R: Router, **kwargs):
        R.write_response("Not implemented", code=400, content_type="text/plain")


    @staticmethod
    def getRequiredParams() -> Dict[str, Type | Tuple]:

        return {
            "sort_type": str,
            "sort_direction": int,
            "offer_count": int,
            "offset": int
        }

