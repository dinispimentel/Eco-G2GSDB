from __future__ import annotations

from typing import Tuple, Type, Dict, Iterable, List, Union

from . import BasicController
from ..RedisCache import RedisCache


class BlackList(BasicController.BasicController):
    from src.routing import Router
    @staticmethod
    def POST(R: Router, jbody: dict = None):

        mp = BlackList.check_params_missing(jbody)
        if len(mp) > 0:
            R.missingParams(mp)
            return

        bpt = BlackList.check_param_type(jbody)
        if len(bpt) > 0:
            R.badParamsTypes(bpt)
            return

        bl_dict = {}
        blt = jbody.get('black_list_titles')
        if isinstance(blt, str):
            blt = [blt]

        for t in blt:
            bl_dict.update({t: True})

        RedisCache.saveBlackList(bl_dict)


        return R.actionSucceeded(f'{len( list(bl_dict.keys()) )} titles were added to the Blacklist')

    @staticmethod
    def getRequiredParams() -> Dict[str, Type | Tuple]:
        return {
            "black_list_titles": (Iterable, str)
        }