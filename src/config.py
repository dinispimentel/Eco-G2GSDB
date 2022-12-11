
class Config:

    CACHEDIR = "/home/dp/Desktop/Eco-G2GSDB/src/cache/"

    class Proxying:

        TIME_OUT = (5, 5)  # write, read
        REUSABILITY_TIMEOUT = 10  # secs
        WAIT_FOR_PROXIES_TO_BE_REUSABLE_TIMER = 30
        TIME_OUT_STACKABLE_LOCK = 30  # isto * num de tentativas em segundos
        TOO_MANY_REQUESTS_STACKABLE_LOCK = 60
        FATAL_LOCK = 30

        class StrikeLimit:
            TIME_OUT = 7
            FORBIDDEN = 3
            TOO_MANY_REQUESTS = 10
            FATAL = 3

        class Files:
            PROXY_ORCHESTRATOR_CACHE = "/home/dp/Desktop/Eco-G2GSDB/src/cache/" + "proxy_orchestrator.json"

    class ENV:
        URL_PPREFIX = "http://"
        LOCAL_IP = "192.168.0.120"

    class G2G:
        SERVICE_ID = "lgc_service_5"

        class BrandOffering:
            QUERY_SIZE = 10
            INSTANCES = 20
            STATIC_MIN_OFFER_COUNT = 15  # O Scraper não permite scrapar account categories com menos doq estas offers


        class Pricing:
            CURRENCY = "EUR"
            COUNTRY = "PT"
            MAX_QUERY = 20  # 5 eraoq tava nos testes
            ALLOWED_CURRENCIES = ['EUR', 'USD']

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
            COUNTRIES = ["ar", "us", "pt"]
            EXRATES_COUNTRIES_CURRENCIES = ["ARS", "USD", "EUR"]  # é necessário conter todas as moedas dos países acima

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
        ALLOWED_CURRENCIES = ["EUR", "USD", "ARS", "TRY"]

    class Redis:
        HOST = 'localhost'
        PORT = 6379

        class DBS:
            APP_IDS = 13
            BLACK_LIST_DB = 14




    @staticmethod
    def buildExRatesURL(path: str):
        return Config.ENV.URL_PPREFIX + Config.ENV.LOCAL_IP + ":" + str(Config.ExRates.PORT) + path
