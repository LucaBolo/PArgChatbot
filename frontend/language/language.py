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
            emb = np.array(json.load(f).values())
    
    else:
        emb = model.encode(sentences, convert_to_numpy = True)

    return emb


def get_most_similar_sentence(user_msg: str, kb: 'list[str]'):
    '''Finds the closest sentence embedding to the user 
    message in terms of Bray-Curtis similarity'''
    
    kb_embeddings = get_embeddings(kb, 'embs.json')
    user_embedding = get_embeddings(user_msg)
    
    distances = [braycurtis(user_embedding, kb_embedding) for kb_embedding in kb_embeddings]

    return kb[np.argmin(distances)]
    


#if __name__ == '__main__':
#    import requests

#    r = requests.get("http://127.0.0.1:5000/sentences")

#    kb = r.json()["data"]

#    print(get_most_similar_sentence("In the past, I had crippling mastocystosis", kb))
