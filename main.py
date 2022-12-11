from functools import partial
from http.server import HTTPServer
import random

from src.ProxyOrchestrator import ProxyOrchestrator
from src.proxies import PROXIES_SOCKS5
from src.DPHTTPRequestHandler import DPHTTPRequestHandler
from src.G2G.G2GData import G2GData

MSGS = {
    "null_json": '{"status": "error", msg: "The JSON received did not contain the skin property on top level."}'
}



PROXIES = PROXIES_SOCKS5
random.shuffle(PROXIES)


if __name__ == '__main__':
    print("init")
    G2GData = G2GData()
    PO = ProxyOrchestrator.build_from_raw(PROXIES, method='socks5')
    partial(DPHTTPRequestHandler, )
    webServer = HTTPServer(("192.168.0.128", 8081), )

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        print("Server closed")

