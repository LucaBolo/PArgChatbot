from sentence_transformers import SentenceTransformer
from torch import argmin, Tensor
from scipy.spatial.distance import braycurtis
import json, os

def get_most_similar_sentence(user_msg: str, kb: 'list[str]'):
    '''Finds the closest sentence embedding to the user 
    message in terms of Bray-Curtis similarity'''
    model = SentenceTransformer("paraphrase-mpnet-base-v2")


    if not os.path.exists('embs.json'):
        kb_embeddings = model.encode(kb, convert_to_tensor=True)
        embedding_obj = {s: kb_embedding.tolist() for s, kb_embedding in zip(kb, kb_embeddings)}
        
        with open(os.path.join(os.getcwd(),'embs.json'), 'w') as f:
            json.dump(embedding_obj, f)
    else:
        with open(os.path.join(os.getcwd(),'embs.json'), 'r') as f:
            kb_embeddings = Tensor(list(json.load(f).values()))    

    user_embedding = model.encode(user_msg, convert_to_tensor=True)

    
    distances = Tensor([braycurtis(user_embedding, kb_embedding) for kb_embedding in kb_embeddings]) 

    return kb[argmin(distances)]
    


#if __name__ == '__main__':
#    import requests

#    r = requests.get("http://127.0.0.1:5000/sentences")

#    kb = r.json()["data"]

#    print(get_most_similar_sentence("In the past, I had crippling mastocystosis", kb))
