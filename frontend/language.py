from sentence_transformers import SentenceTransformer, util


def get_most_similar_sentence(user_msg: str, kb: 'list[str]'):

    model = SentenceTransformer("paraphrase-mpnet-base-v2")

    # kb embeddings should not be computed everytime but cached
    kb_embeddings = model.encode(kb, convert_to_tensor=True)
    user_embedding = model.encode(user_msg, convert_to_tensor=True)

    # they don't exactly use cosine similarity
    cosine_scores = util.cos_sim(user_embedding, kb_embeddings) 

    print(kb)
    print(cosine_scores)
    


if __name__ == '__main__':
    import requests

    r = requests.get("http://127.0.0.1:5000/sentences")

    kb = r.json()["data"]

    get_most_similar_sentence("In the past, I had crippling mastocystosis", kb)
