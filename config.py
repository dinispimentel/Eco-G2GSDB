


class Config:

    CACHEDIR = "./cache/"

    class ENV:
        URL_PPREFIX = "http://"
        LOCAL_IP = "192.168.0.120"

    class G2G:
        SERVICE_ID = "lgc_service_5"

        class BrandOffering:
            QUERY_SIZE = 10
            INSTANCES = 20

        class Pricing:
            CURRENCY = "EUR"
            COUNTRY = "PT"

        class FilterOffer:
            OVERALL_DESC_FACTOR = 0.7
            OVERALL_TITLE_FACTOR = 0.3
            VALID_OFFER_OVERALL_THRESHOLD = 0

        class Offering:
            INSTANCES = 50
            QUERY_SIZE = 2

    class SteamDB:

        class AppIDing:
            INSTANCES = 100

        class AppPricing:
            INSTANCES = 10
            QUERY_SIZE = 5  # Parece não suportar > 1
            FORBIDDEN_TIMEOUT = int(60*3)  # em segundos
            DELAY_CONFIG = {
                "delay": int(60),  # em segundos
                "instances_before_delay": 60  # num de threads que podem seguir antes do delay
            }

    class OfferBooking:

        class FILES:


            @staticmethod
            def getPriced(testing=False):

                if testing:
                    return Config.CACHEDIR + "offerbook-priced-testing.json"

                return Config.CACHEDIR + "offer-priced.json"

            @staticmethod
            def getOrdered(testing=False):

                if testing:
                    return Config.CACHEDIR + "offers-ordered-testing.json"
                return Config.CACHEDIR + "offers-ordered.json"

            @staticmethod
            def getAppIDed(testing=False):

                if testing:
                    return Config.CACHEDIR + "offer-book-priced-appided-testing.json"
                return Config.CACHEDIR + "offer-book-priced-appided.json"


            @staticmethod
            def getSteamPriced(testing=False):
                if testing:
                    return Config.CACHEDIR + "offer-book-steampriced-testing.json"

                return Config.CACHEDIR + "offer-book-steampriced.json"

    class ExRates:
        PORT = 8085
        BASE = "EUR"





    @staticmethod
    def buildExRatesURL(path: str):
        return Config.ENV.URL_PPREFIX + Config.ENV.LOCAL_IP + ":" + str(Config.ExRates.PORT) + path
