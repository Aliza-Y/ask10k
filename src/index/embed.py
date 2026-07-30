from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-small-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_passages(texts: list[str]) -> np.ndarray:
    return get_model().encode(texts, batch_size=64,
                              normalize_embeddings=True, show_progress_bar=True)


def embed_query(text: str) -> np.ndarray:
    return get_model().encode(QUERY_PREFIX + text, normalize_embeddings=True)