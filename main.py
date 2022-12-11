import http
import socketserver
from functools import partial
from http.server import HTTPServer
import random
from threading import Thread

from src.ProxyOrchestrator import ProxyOrchestrator
from src.proxies import PROXIES_SOCKS5
from src.DPHTTPRequestHandler import DPHTTPRequestHandler
from src.G2G.G2GData import G2GData

MSGS = {
    "null_json": '{"status": "error", msg: "The JSON received did not contain the skin property on top level."}'
}



PROXIES = PROXIES_SOCKS5
random.shuffle(PROXIES)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

if __name__ == '__main__':
    print("init")
    G2GData = G2GData()
    PO = ProxyOrchestrator.build_from_raw(PROXIES, method='socks5')
    RH = partial(DPHTTPRequestHandler, G2GData, PO)
    print("Binding..")
    webServer = ThreadedHTTPServer(("192.168.0.120", 8081), RH)

    try:
        webServer_Thread = Thread(target=webServer.serve_forever)

        webServer_Thread.start()
        print("Started")
        webServer_Thread.join()

    except KeyboardInterrupt:
        webServer.server_close()
        print("Closed")

