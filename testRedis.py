

from src.RedisCache import RedisCache

RedisCache.saveBlackList({"Roblox": True, "Evertale": True, "Pokemon Masters": True, "Clash Royale": True,
                          "Call of Duty: Mobile - Garena": True})
# print(RedisCache.areBlackList(["EVE", "Factorio"]))

# RedisCache.saveAppIDs({
#     "Factorio": 427520,
#     "EVE Online": 8500
# })
# appIds = RedisCache.getAppIDs(["Factorio", "EVE Online"])
#
# for appId in appIds:
#     print(appId if appId is None else appId.decode("utf-8"))
