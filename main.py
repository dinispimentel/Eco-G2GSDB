
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from G2G.G2GScraper import G2GScraper

MSGS = {
    "null_json": '{"status": "error", msg: "The JSON received did not contain the skin property on top level."}'
}


class DPHTTPRequestHandler(BaseHTTPRequestHandler):

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


if __name__ == '__main__':
    print("init")
    webServer = HTTPServer(("192.168.0.128", 8081), DPHTTPRequestHandler)
    webServer.serve_forever()

