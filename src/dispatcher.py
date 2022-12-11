import os.path

import requests
import json
from src.config import Config

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "secret.json"), "r") as file:
    ENV = json.loads(file.read())

G2GServiceID = "lgc_service_5"


class Dispatcher:

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.g2g.com/',
        'Origin': 'https://www.g2g.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'If-Modified-Since': 'Fri, 30 Sep 2022 09:59:57 GMT',
        'If-None-Match': 'W/2e3d8510d2638ff6d09a9c4b0979798e',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    @staticmethod
    def G2G_getCategories():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.g2g.com/',
            'Origin': 'https://www.g2g.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'If-Modified-Since': 'Fri, 30 Sep 2022 09:59:57 GMT',
            'If-None-Match': 'W/2e3d8510d2638ff6d09a9c4b0979798e',
            # Requests doesn't support trailers
            # 'TE': 'trailers',
        }
        response = requests.get('https://assets.g2g.com/offer/categories.json', headers=headers)
        return json.loads(response.content)

    @staticmethod
    def FxMarket_getForexQuotes(form_cur):
        headers = {
            'Accept': 'application/json',
            'Authorization': 'DsC9gzJQdF82n3tzOyDV02Q1',
        }

        params = {

        }

        response = requests.get('https://fxmarketapi.com/apilive?api_key={}&currency={}.json'.format(ENV["fxmarketapi"],
                                                                                                     form_cur),
                                params=params,
                                headers=headers)
        return response

    @staticmethod
    def Steam_GetAppIDPrice(appID, country):
        response = requests.get("https://store.steampowered.com/api/appdetails?appids={}&cc={}&filters=price_overview"
                                .format(appID, country))
        return response

    @staticmethod
    def SteamDB_GetAppIDFromTitle(title):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://steamdb.info/',
            'Origin': 'https://steamdb.info',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        }
        params = {
            'x-algolia-agent': 'SteamDB Autocompletion',
            'x-algolia-application-id': '94HE6YATEI',
            'x-algolia-api-key': '338033d8e504a8a3f98452c637d713b9',
            'hitsPerPage': '15',
            'attributesToSnippet': 'null',
            'attributesToHighlight': 'name',
            'attributesToRetrieve': 'name,objectID,lastUpdated',
            'query': title,
        }
        return requests.get('https://94he6yatei-dsn.algolia.net/1/indexes/steamdb/', params=params, headers=headers)

    @staticmethod
    def G2G_getBrandsOffer(stringified_brands):
        params = {"service_id": G2GServiceID, "id": stringified_brands}
        headers = {"Content-Type": "application/json"}
        url = "https://sls.g2g.com/offer/brand_offer_count"

        return requests.request("GET", url, headers=headers, params=params)



    @staticmethod
    def G2G_getLowestPrices(brand, maxQuerySize):

        params = {
            'service_id': Config.G2G.SERVICE_ID,
            'brand_id': brand,
            'sort': 'lowest_price',
            'page_size': maxQuerySize,
            'currency': Config.G2G.Pricing.CURRENCY,
            'country': Config.G2G.Pricing.COUNTRY
        }

        res = requests.get('https://sls.g2g.com/offer/search', params=params)
        j = json.loads(res.content)
        return j

    @staticmethod
    def ExRates_getRates():
        res = requests.get(Config.buildExRatesURL("/getExRates"))
        return json.loads(res.content)

    @staticmethod
    def ExRates_getBase():
        res = requests.get(Config.buildExRatesURL("/getBase"))
        o = json.loads(res.content)
        if "base" in o:
            return o["base"]
        else:
            raise Exception("No base retrieved")

    @staticmethod
    def ExRates_forceUpdate(base=None, currencies=None):
        payload = {}
        if base:
            payload.update({"base": base})
        if currencies:
            payload.update({"currencies": currencies})

        res = requests.post(Config.buildExRatesURL("/forceUpdate"), json=payload)
        if 200 > res.status_code >= 299:
            raise Exception(f"Não foi possível dar force update.\n {res.content}")


