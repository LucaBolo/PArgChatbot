from sentence_transformers import SentenceTransformer
from torch import argmin, Tensor
from scipy.spatial.distance import braycurtis

def get_most_similar_sentence(user_msg: str, kb: 'list[str]'):

    model = SentenceTransformer("paraphrase-mpnet-base-v2")

    # kb embeddings should not be computed everytime but cached
    kb_embeddings = model.encode(kb, convert_to_tensor=True)
    user_embedding = model.encode(user_msg, convert_to_tensor=True)

    
    distances = Tensor([braycurtis(user_embedding, kb_embedding) for kb_embedding in kb_embeddings]) 

    return kb[argmin(distances)]
    


#if __name__ == '__main__':
#    import requests

#    r = requests.get("http://127.0.0.1:5000/sentences")

#    kb = r.json()["data"]

#    print(get_most_similar_sentence("In the past, I had crippling mastocystosis", kb))
