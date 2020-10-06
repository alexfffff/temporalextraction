from flask import Flask
from flask import request
from flask import send_from_directory
from flask_cors import CORS

from lib_control import CogCompTimeBackend


class CogCompTimeDemoService:

    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.backend = CogCompTimeBackend()

    @staticmethod
    def handle_root(path):
        if path == "" or path is None:
            path = "index.html"
        return send_from_directory('./frontend', path)

    @staticmethod
    def handle_index():
        return send_from_directory('./frontend', 'index.html')

    def handle_request(self):
        args = request.get_json()
        text = args['text']
        order = self.backend.build_graph(text)
        return {
            "result": order,
        }

    def start(self, localhost=False, port=80, ssl=False):
        self.app.add_url_rule("/", "", self.handle_index)
        self.app.add_url_rule("/<path:path>", "<path:path>", self.handle_root)
        self.app.add_url_rule("/request", "request", self.handle_request, methods=['POST', 'GET'])
        if ssl:
            if localhost:
                self.app.run(ssl_context='adhoc', port=port)
            else:
                self.app.run(host='0.0.0.0', port=port, ssl_context='adhoc')
        else:
            if localhost:
                self.app.run(port=port)
            else:
                self.app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    service = CogCompTimeDemoService()
    service.start(localhost=False, port=4014)
