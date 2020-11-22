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

    def tokenized_to_origin_span(self, text, token_list):
        text = text.replace("\n", "")
        token_span = []
        pointer = 0
        for token in token_list:
            while True:
                if token[0] == text[pointer]:
                    start = pointer
                    end = start + len(token) - 1
                    pointer = end + 1
                    break
                else:
                    pointer += 1
            token_span.append([start, end])
        return token_span

    def handle_request(self):
        args = request.get_json()
        text = args['text']
        order = self.backend.build_graph(text)
        return {
            "result": order,
        }

    def handle_json_request(self):
        args = request.get_json()
        token_to_span = self.tokenized_to_origin_span(args['text'], args['tokens'])
        tokens = args["tokens"]
        sent_ends = []
        for sent_end_char_id in args["sentences"]["sentenceEndPositions"]:
            for i, t in enumerate(token_to_span):
                if t[1] + 1 == sent_end_char_id:
                    sent_ends.append(i)
                    break
        sent_ends = list(set(sent_ends))
        accumulator = 0
        token_to_send_id = {}
        for i in range(0, len(tokens)):
            token_to_send_id[i] = accumulator
            if i in sent_ends:
                accumulator += 1
        sentences = []
        cur_sent_id = 0
        sentence = []
        for t in token_to_send_id:
            if token_to_send_id[t] == cur_sent_id:
                sentence.append(tokens[t])
            else:
                sentences.append(sentence)
                cur_sent_id = token_to_send_id[t]
                sentence = [tokens[t]]
        sentences.append(sentence)
        sentence_minus_val = {}
        accu = 0
        for i in range(0, len(sentences)):
            sentence_minus_val[i] = accu + len(sentences[i])
            accu = len(sentences[i])
        views = args["views"]
        event_view = None
        for view in views:
            if view["viewName"] == "Event_extraction":
                event_view = view
                break
        if event_view is None:
            return args
        event_triggers = []
        for constituent in event_view["viewData"][0]['constituents']:
            start = constituent["start"]
            if "properties" in constituent:
                event_triggers.append((constituent['properties']['sentence_id'], start))
        event_triggers = list(set(event_triggers))
        formatted_events = []
        for event in event_triggers:
            formatted_events.append(event)
        relative_order = self.backend.build_graph_with_events(sentences, formatted_events, dct="2020-10-01")

        return None

    def start(self, localhost=False, port=80, ssl=False):
        self.app.add_url_rule("/", "", self.handle_index)
        self.app.add_url_rule("/<path:path>", "<path:path>", self.handle_root)
        self.app.add_url_rule("/request", "request", self.handle_request, methods=['POST', 'GET'])
        self.app.add_url_rule("/request_temporal_json", "request_temporal_json", self.handle_json_request, methods=['POST', 'GET'])
        if ssl:
            if localhost:
                self.app.run(ssl_context='adhoc', port=port)
            else:
                self.app.run(host='0.0.0.0', port=port, ssl_context='adhoc')
        else:
            if localhost:
                self.app.run()
            else:
                self.app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    service = CogCompTimeDemoService()
    service.start(localhost=True)
