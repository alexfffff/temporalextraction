from lib_parser import PretrainedModel, AllenSRL, TimeStruct
from lib_control import get_story, get_verb_index, get_skeleton_phrase
from tracie_model.start_predictor import RelationOnlyPredictor
import random


def read_tokens_file_source(file_id):
    lines = [x.strip() for x in open("kairos_data/input/ltf/{}.ltf.xml".format(file_id)).readlines()]
    all_tokens = []
    cur_tokens = []
    start_char_to_token = {}
    for line in lines:
        if line.startswith("</SEG>"):
            all_tokens.append(cur_tokens)
            cur_tokens = []
        if line.startswith("<TOKEN"):
            start_char = int(line.split()[4].split('"')[1])
            start_char_to_token[start_char] = (len(all_tokens), len(cur_tokens))
            token = line.split()[-1].split(">")[1].split("<")[0]
            cur_tokens.append(token)

    return all_tokens, start_char_to_token


def format_model_phrase(srl, verb_id, surface):
    phrase = ""
    for verb in srl['verbs']:
        if get_verb_index(verb['tags']) == verb_id:
            phrase = get_skeleton_phrase(verb['tags'], srl['words'])
    if phrase == "":
        phrase = surface
    return phrase

def process_kairos():
    srl_model = PretrainedModel(
        'https://s3-us-west-2.amazonaws.com/allennlp/models/srl-model-2018.05.25.tar.gz',
        'semantic-role-labeling'
    ).predictor()
    lines = [x.strip() for x in open("kairos_data/output/coref/event.cs").readlines()]
    event_id_to_token_ids = {}
    added_story_ids = set()
    all_sentences = []
    predictor = RelationOnlyPredictor()
    f_out = open("results.txt", "w")
    for line in lines:
        groups = line.split("\t")
        event_id = groups[0]
        if groups[1] == "mention.actual":
            if event_id not in event_id_to_token_ids:
                event_id_to_token_ids[event_id] = []
            file_id = groups[3].split(":")[0]
            start_char = int(groups[3].split(":")[1].split("-")[0])
            doc_tokens, start_char_to_token = read_tokens_file_source(file_id)
            if file_id not in added_story_ids:
                added_story_ids.add(file_id)
                for tokens in doc_tokens:
                    all_sentences.append(tokens)
            token_id = start_char_to_token[start_char]
            event_id_to_token_ids[event_id].append(
                [doc_tokens, token_id]
            )
    all_srl_map = {}
    for i, tokens in enumerate(all_sentences):
        if i % 10 == 0:
            print("SRL Processed {}".format(str(float(i) / len(all_sentences))))
        all_srl_map[" ".join(tokens)] = srl_model.predict_tokenized(tokens)
    all_event_ids = list(event_id_to_token_ids.keys())
    for i in range(0, len(all_event_ids)):
        for j in range(i+1, len(all_event_ids)):
            i_events = event_id_to_token_ids[all_event_ids[i]]
            j_events = event_id_to_token_ids[all_event_ids[j]]
            random.shuffle(i_events)
            random.shuffle(j_events)
            if len(i_events) > 5:
                i_events = i_events[:5]
            if len(j_events) > 5:
                j_events = j_events[:5]

            to_process = []
            for i_t in i_events:
                for j_t in j_events:
                    story_raw_i = i_t[0]
                    story_raw_j = j_t[0]
                    i_srls = []
                    for t in story_raw_i:
                        i_srls.append(all_srl_map[" ".join(t)])
                    j_srls = []
                    for t in story_raw_j:
                        j_srls.append(all_srl_map[" ".join(t)])
                    story_i = get_story(i_srls, max_len=150)
                    story_j = get_story(j_srls, max_len=150)

                    phrase_i = format_model_phrase(i_srls[i_t[1][0]], i_t[1][1], story_raw_i[i_t[1][0]][i_t[1][1]])
                    phrase_j = format_model_phrase(j_srls[j_t[1][0]], j_t[1][1], story_raw_j[j_t[1][0]][j_t[1][1]])
                    instance = "event: {} starts before {} story: {} \t nothing".format(phrase_i, phrase_j, story_i + " " + story_j)

                    to_process.append(instance)
            results = predictor.predict(to_process)
            total_before = 0.0
            total_after = 0.0
            for r in results:
                total_before += r[0]
                total_after += r[0]
            prob_before = total_before / (total_before + total_after)
            prob_after = total_after / (total_before + total_after)
            if prob_before > prob_after:
                label = "TEMPORAL_BEFORE"
                prob = prob_before
            else:
                label = "TEMPORAL_AFTER"
                prob = prob_after
            f_out.write("{}\t{}\t{}\t{}\n".format(all_event_ids[i], label, all_event_ids[j], str(prob)))

            key = "{}-{}".format(all_event_ids[i], all_event_ids[j])
            print("Done: " + key)


process_kairos()