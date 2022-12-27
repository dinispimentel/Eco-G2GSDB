import time
from typing import Tuple, Callable

from src.G2G.G2GOfferBook import OfferBook


class G2GData:

    def __init__(self, offerbook: OfferBook = None, lastUpdate=None, status=None, progress=None):
        self.locked: bool = False
        self.offerbook: OfferBook = offerbook or OfferBook.loadFromFile("/home/dp/Desktop/Eco-G2GSDB/src/cache/myofferbook.json")
        # OfferBook.loadFromFile("/home/dp/Desktop/Eco-G2GSDB/src/cache/myofferbook.json")
        #


        self.lastUpdate: float = lastUpdate
        self.status: str = status or "Idle"
        # self.progress: Callable[[float, int], bool] = progress  # em ratio [0 ; 1]

    def tryRetrieveOfferbook(self) -> Tuple[bool, OfferBook or str]:
        if self.locked:
            return False, self.status
        else:
            return True, self.offerbook

    def lock(self, status="Processing..."):
        self.locked = True
        self.status = status
        self.timeUpdate()

    def unlock(self):
        self.locked = False
        self.status = "Idle"
        self.timeUpdate()

    def timeUpdate(self):
        self.lastUpdate = time.time()

    def setStatus(self, newStatus: str):
        self.status = newStatus