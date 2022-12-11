import json
from http.server import BaseHTTPRequestHandler

from G2G.G2GScraper import G2GScraper
from src.ProxyOrchestrator import ProxyOrchestrator


class DPHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, dmdata, PO, *args, **kwargs):
        from .routing import Router
        # self.dmarket_data_update_timestamp = getPersistantData().get('dmarket_data_update_timestamp')
        # self.current_status = getPersistantData().get('c') or "inited"
        from src.G2G.G2GOfferBook import OfferBook
        from src.G2G.G2GData import G2GData
        self.G2GData: G2GData = dmdata
        # self.PO = getPersistantData().get('PO') or ProxyOrchestrator.build_from_raw(PROXIES,
        #                                                                             method='socks5')
        self.PO: ProxyOrchestrator = PO
        self.router = Router(self)
        # self.setPersistantData = setPersistantData
        # self.getPersistantData = getPersistantData
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
        if self.path == '/getUpdatedOfferBook':
            G2GScraper.updateAccountCache()
            ob = G2GScraper.getOffers(False)
            self.write_response(ob.toJSON())

    def do_POST(self):
        if self.path == "/scrapAccount":
            body = self.rfile.read()
            pbody = json.loads(body)
            if not pbody["account"]:
                self.write_response(MSGS["null_json"])
                return
    def write_response(self, content):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(str(content).encode("utf-8"))