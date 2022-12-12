
import hashlib
from typing import List

import redis

from src.config import Config

r = redis.Redis(host=Config.Redis.HOST, port=Config.Redis.PORT, db=13)  # para os appIDs dos títulos 13

r2 = redis.Redis(host=Config.Redis.HOST, port=Config.Redis.PORT, db=14)  # as BlackLists 14

class RedisCache:

    @staticmethod
    def __hash_it(txt):
        return hashlib.sha1(str(txt).encode("utf-8")).hexdigest()

    @staticmethod
    def saveAppIDs(mapping_unhashed: dict[str, int]):
        # mapping_unhashed = {title => appID}
        if not mapping_unhashed or len(mapping_unhashed.keys()) < 1:

            return

        r.mset(mapping_unhashed)

    @staticmethod
    def getAppIDs(titles: List[str]):

        appids = r.mget(titles)

        return appids

    @staticmethod
    def saveBlackList(mapping_unhashed: dict[str, bool]):
        if not mapping_unhashed or len(mapping_unhashed.keys()) < 1:

            return
        for k, v in mapping_unhashed.items():
            if type(v) == type(True):
                mapping_unhashed.update({k: str(v)})

        r2.mset(mapping_unhashed)

    @staticmethod
    def areBlackList(titles: List[str]) -> dict[str, bool]:

        title_bool = {}

        bools = r2.mget(titles)

        i = 0
        for t in titles:
            print(bools[i])
            title_bool.update({str(t): (False if bools[i] is None else (False if bools[i].decode("utf-8") == 'False' or bools[i].decode("utf-8") == False else True))})
            i += 1

        return title_bool