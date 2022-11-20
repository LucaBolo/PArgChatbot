from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import braycurtis
import numpy as np
import json, os

def get_embeddings(sentences: 'list[str]', embedding_file = None):
    model = SentenceTransformer("paraphrase-mpnet-base-v2")

    if embedding_file and not os.path.exists(embedding_file):

        emb = model.encode(sentences, convert_to_numpy = True)
        embedding_obj = {s: kb_embedding.tolist() for s, kb_embedding in zip(sentences, emb)}
        with open(os.path.join(os.getcwd(), embedding_file), 'w') as f:
            json.dump(embedding_obj, f)
    elif embedding_file and os.path.exists(embedding_file):
        
        with open(os.path.join(os.getcwd(),embedding_file), 'r') as f:
            emb = list(json.load(f).values())
            emb = np.array(emb)
            
    
    else:
        emb = model.encode(sentences, convert_to_numpy = True)

    return emb


def get_most_similar_sentence(user_msg: str, kb: 'list[str]'):
    '''Finds the closest sentence embedding to the user 
    message in terms of Bray-Curtis similarity'''
    
    current_module_path = os.path.dirname(os.path.realpath(__file__))
    kb_embeddings = get_embeddings(kb, os.path.join(current_module_path, 'kb_embs.json'))
    user_embedding = get_embeddings(user_msg)
    
    print(kb_embeddings)
    distances = [braycurtis(user_embedding, kb_embedding) for kb_embedding in kb_embeddings]
    
    index = np.argmin(distances)

    print(distances, distances[index])

    return kb[index]
    

