from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
from numpy.linalg import norm

model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def embed_texts(texts: List[str]) -> List[List[float]]:
    m = get_model()
    embs = m.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return [e.tolist() for e in embs]

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    if norm(a) == 0 or norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (norm(a) * norm(b)))

def rank_books_by_embedding(user_emb: List[float], books: List[dict], top_k: int = 5):
    user_vec = np.array(user_emb)
    results = []
    for book in books:
        if not book.get('embedding'):
            continue
        book_vec = np.array(book['embedding'])
        score = cosine_sim(user_vec, book_vec)
        results.append((score, book))
    results.sort(key=lambda x: x[0], reverse=True)
    return [b for s, b in results[:top_k]]
