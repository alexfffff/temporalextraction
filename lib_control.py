from tracie_model.start_predictor import Predictor
from lib_parser import PretrainedModel
import spacy
import torch
from collections import defaultdict


def get_verb_index(tags):
    for i, t in enumerate(tags):
        if t == "B-V":
            return i
    # There is no verb, abort
    return -1

def get_skeleton_phrase(tags, words):
    ret = ""
    for i, tok in enumerate(words):
        if tags[i] != "O":
            ret += tok + " "
    return ret.strip()


class Graph:
    def __init__(self, vertices):
        self.graph = defaultdict(list)
        self.V = vertices

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def isCyclicUtil(self, v, visited, recStack):

        # Mark current node as visited and
        # adds to recursion stack
        visited[v] = True
        recStack[v] = True

        # Recur for all neighbours
        # if any neighbour is visited and in
        # recStack then graph is cyclic
        for neighbour in self.graph[v]:
            if visited[neighbour] == False:
                if self.isCyclicUtil(neighbour, visited, recStack) == True:
                    return True
            elif recStack[neighbour] == True:
                return True

        # The node needs to be poped from
        # recursion stack before function ends
        recStack[v] = False
        return False

    # Returns true if graph is cyclic else false
    def isCyclic(self):
        visited = [False] * self.V
        recStack = [False] * self.V
        for node in range(self.V):
            if visited[node] == False:
                if self.isCyclicUtil(node, visited, recStack) == True:
                    return True
        return False

    # A recursive function used by topologicalSort
    def topologicalSortUtil(self, v, visited, stack):

        # Mark the current node as visited.
        visited[v] = True

        # Recur for all the vertices adjacent to this vertex
        for i in self.graph[v]:
            if visited[i] == False:
                self.topologicalSortUtil(i, visited, stack)

                # Push current vertex to stack which stores result
        stack.insert(0, v)

        # The function to do Topological Sort. It uses recursive

    # topologicalSortUtil()
    def topologicalSort(self):
        # Mark all the vertices as not visited
        visited = [False] * self.V
        stack = []

        # Call the recursive helper function to store Topological
        # Sort starting from all vertices one by one
        for i in range(self.V):
            if visited[i] == False:
                self.topologicalSortUtil(i, visited, stack)

                # Print contents of stack
        return stack


class CogCompTimeBackend:

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.predictor = Predictor()
        self.srl_model = PretrainedModel(
            'https://s3-us-west-2.amazonaws.com/allennlp/models/srl-model-2018.05.25.tar.gz',
            'semantic-role-labeling'
        ).predictor()
        if self.device == 'cuda':
            self.srl_model._model = self.srl_model._model.cuda()
        self.spacy_model = spacy.load("en_core_web_sm", disable='ner')

    def parse_srl(self, text):
        doc = self.spacy_model(text)
        sentences = []
        for sent in doc.sents:
            toks = []
            for tok in sent:
                toks.append(str(tok))
            sentences.append(toks)

        srl_objs = []
        for sentence in sentences:
            srl_obj = self.srl_model.predict_tokenized(sentence)
            srl_objs.append(srl_obj)
        return sentences, srl_objs

    def extract_events(self, srl_objs):
        ret = {}
        cur_id = 0
        for i, obj in enumerate(srl_objs):
            for verb in obj['verbs']:
                verb_idx = get_verb_index(verb['tags'])
                if verb_idx > 0:
                    ret[cur_id] = [i, verb_idx, obj['words'][verb_idx]]
                    cur_id += 1
        return ret, cur_id

    def format_model_phrase(self, event, srl):
        phrase = ""
        for verb in srl['verbs']:
            if get_verb_index(verb['tags']) == event[1]:
                phrase = get_skeleton_phrase(verb['tags'], srl['words'])
        return phrase

    def build_graph(self, text):
        sentences, srl_objs = self.parse_srl(text)
        for i in range(0, len(sentences)):
            for j in range(0, len(sentences[i])):
                assert sentences[i][j] == srl_objs[i]['words'][j]
        event_map, event_count = self.extract_events(srl_objs)
        all_event_ids = list(event_map.keys())
        to_process_instances = []
        for event_id_i in all_event_ids:
            for event_id_j in all_event_ids:
                phrase_i = self.format_model_phrase(event_id_i, srl_objs[event_id_i[0]])
                phrase_j = self.format_model_phrase(event_id_j, srl_objs[event_id_j[0]])
                instance = "event: {} starts before {} story: \t nothing".format(phrase_i, phrase_j)
                to_process_instances.append(instance)

        results = self.predictor.predict(to_process_instances)
        print(results)
        graph = Graph(event_count)


backend = CogCompTimeBackend()
backend.build_graph("They became friends when they attended the same university 9 years ago. Now they are planning their wedding this June.")