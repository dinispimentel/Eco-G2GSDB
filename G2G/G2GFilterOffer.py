
from config import Config

from ecolib.logger import lg as logging


class FilterOffer:



    def __init__(self, offer, title_kwds, description_kwds, title_kwds_black, description_kwds_black, extreme_black,
                 extreme_white):
        self.offer = offer
        self.title_kwds = title_kwds
        self.description_kwds = description_kwds
        self.title_kwds_black = title_kwds_black
        self.description_kwds_black = description_kwds_black
        self.extreme_black = extreme_black
        self.extreme_white = extreme_white
        self.overall_score = -1

        self.extremed = False
        self.price = float(offer["display_price"])

    def performFiltering(self):



        title = str(self.offer["title"]).lower()
        description = str(self.offer["description"]).lower()
        brand_id = str(self.offer["brand_id"])
        title_points = 0
        description_points = 0

        for word in self.title_kwds:
            if str().__contains__(str(word[0]).lower()):
                # logging.info(brand_id + "title contains: +" + str(word[0]).lower())
                title_points += int(word[1])



        for word in self.description_kwds:
            if str(description).__contains__(str(word[0]).lower()):
                # logging.info(brand_id + "desc contains: +" + str(word[0]).lower())
                description_points += int(word[1])

        for word in self.title_kwds_black:
            if str(title).__contains__(str(word[0])):
                # logging.info(brand_id + "title contains: -" + str(word[0]).lower())
                title_points -= int(word[1])

        for word in self.description_kwds_black:
            if str(description).__contains__(str(word[0]).lower()):
                # logging.info(brand_id + "desc contains: -" + str(word[0]).lower())
                description_points -= int(word[1])

        for word in self.extreme_black:
            if str(description).__contains__(str(word).lower()) or \
                    str(title).__contains__(str(word).lower()):
                logging.info(brand_id + "title/desc contains black extreme: --" + str(word).lower())
                self.overall_score = -5000
                self.extremed = word
                return None

        for word in self.extreme_white:
            if str(description).__contains__(str(word).lower()) or \
                    str(title).__contains__(str(word).lower()):
                logging.info(brand_id + "title/desc contains white extreme: --" + str(word).lower())
                self.overall_score = 5000
                self.extremed = word
                return self


        self.overall_score = (title_points + description_points)

        logging.info(brand_id + " overall score: " + str(self.overall_score))
        if self.overall_score > Config.G2G.FilterOffer.VALID_OFFER_OVERALL_THRESHOLD:
            return self
        else:

            logging.warning("Oferta não cumpria requisitos de filtragem:")
            logging.warning(str(self.offer))
            logging.warning("Found extremed: " + str(self.extremed))
            return None
