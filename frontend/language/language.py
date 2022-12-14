from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import braycurtis
import numpy as np
import json, os


def get_thresholds():
    return {
        # thresholds that give best f1 score according to threshold tuning
        # in A privacy-preserving dialogue system based on argumentation paper
            "paraphrase-mpnet-base-v2": 0.70,
            "stsb-mpnet-base-v2": 0.60,
            "paraphrase-multilingual-mpnet-base-v2": 0.65
        }

def get_embeddings(sentences: 'list[str]', model_name="paraphrase-mpnet-base-v2", embedding_file = None):
    model = SentenceTransformer(model_name)
    
    if embedding_file and not os.path.exists(embedding_file):

        emb = model.encode(sentences, convert_to_numpy = True)
        embedding_obj = {s: kb_embedding.tolist() for s, kb_embedding in zip(sentences, emb)}
        with open(os.path.join(os.getcwd(), embedding_file), 'w') as f:
            json.dump(embedding_obj, f)
    elif embedding_file and os.path.exists(embedding_file):

        with open(os.path.join(os.getcwd(),embedding_file), 'r') as f:
            obj = json.load(f)
            sentences = list(obj.keys())
            emb = np.array(list(obj.values()))

            
    
    else:
        # this is the case when we want to create
        # temporary embeddings for predictions, don't want to store a file
        emb = model.encode(sentences, convert_to_numpy = True)
        

    return sentences, emb


def get_most_similar_sentence(user_msg: str, kb: 'list[str]'):
    '''Finds the closest sentence embeddings to the user 
    message in terms of Bray-Curtis distance and a tuned threshold'''
    
    current_module_path = os.path.dirname(os.path.realpath(__file__))

    kb, kb_embeddings = get_embeddings(kb, embedding_file=os.path.join(current_module_path, 'kb_embs.json'))
    _, user_embedding = get_embeddings(user_msg)

    threshold = get_thresholds()["paraphrase-mpnet-base-v2"]
    similar = []
    for i, kb_embedding in enumerate(kb_embeddings):

        similar.append( (kb[i], 1 - braycurtis(user_embedding, kb_embedding)) )
    # keep only the sentences above the threshold in similarity
    
    # print(s_distances)
    similar = list(filter(lambda s_distance : s_distance[1] >= threshold, similar))
    print(similar)
    return list(map(lambda s_distance : s_distance[0] , similar))
    

def get_intent(user_msg: str):
    '''Finds the closest sentence in the dialogue act
    sentences and returns the corresponding intet (yes, no, dno)'''

    current_module_path = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(current_module_path, "dialogue_act.json")) as f:
        dialogue_acts = json.load(f)


    dialogue_acts_sentences = [s for _, dialogue_act in dialogue_acts.items() for s in dialogue_act]
    sentences, sentences_embs = get_embeddings(dialogue_acts_sentences, embedding_file=os.path.join(current_module_path, "dialogue_act_embs.json"))
    _, user_embedding = get_embeddings(user_msg)

    closest_sentence = max([(sentences[i], 1 - braycurtis(sentence_emb, user_embedding)) for i, sentence_emb in enumerate(sentences_embs)], key=lambda x: x[1])
    threshold = get_thresholds()["paraphrase-mpnet-base-v2"]
    for k in dialogue_acts.keys():
        print(closest_sentence)
        if closest_sentence[0] in dialogue_acts[k] and closest_sentence[1] >= threshold:
            
            return k

    
    return None