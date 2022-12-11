import json
from http.server import BaseHTTPRequestHandler

from src.G2G.G2GScraper import G2GScraper
from src.ProxyOrchestrator import ProxyOrchestrator


class DPHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, g2gdata, PO, *args, **kwargs):
        from .routing import Router

        from src.G2G.G2GData import G2GData
        self.G2GData: G2GData = g2gdata

        self.PO: ProxyOrchestrator = PO
        self.router = Router(self)

        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.router.GET()

    def do_POST(self):
        self.router.POST()

    def write_response(self, content):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(str(content).encode("utf-8"))

ERRORS = {
    "null_json": {"success": False, "msg": "The JSON received did not contain the required params."},
    "internal_error": {"success": False, "msg": "Internal error occurred"},
    "data_locked": {"success": False, "msg": "Data is locked."},
    "offer_book_missing_flag": {"success": False,
                                "msg": "Internal OfferBook can't proceed to this action (Missing Flags)."},
    "offer_book_currency_mismatch": {"success": False, "msg": "One of the currencies is not equal to the other.\n"
                                                              "Please Convert:"},
    "bad_params": {"success": False, "msg": "Bad params."}
}
SUCCESSES = {
    "action_succeded": {"success": True, "msg": "Action performed successfuly."}
}