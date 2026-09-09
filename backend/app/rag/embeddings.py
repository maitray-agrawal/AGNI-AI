import hashlib
import math
from typing import List
import numpy as np
import logging

logger = logging.getLogger("agni.rag.embeddings")

EMBEDDING_DIM = 384


class LocalEmbedder:
    """Lightweight mathematical vectorizer: deterministic 384-dimensional term and n-gram hashing vectorizer.
    
    Zero external dependencies, offline mathematical vectorization for air-gapped CPU execution.
    Projects semantic token clusters and n-grams into a normalized dense space for cosine retrieval.
    """

    def __init__(self, dim: int = EMBEDDING_DIM):
        self.dim = dim

    def embed_text(self, text: str) -> List[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()

        for idx, word in enumerate(words):
            # Term hash position
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            pos = h % self.dim
            sign = 1.0 if ((h >> 8) & 1) == 0 else -1.0
            
            # Position & frequency weighting
            weight = 1.0 + (1.0 / (1.0 + math.log1p(idx)))
            vec[pos] += sign * weight

            # Bigram feature if available
            if idx > 0:
                bigram = f"{words[idx-1]}_{word}"
                bh = int(hashlib.md5(bigram.encode("utf-8")).hexdigest(), 16)
                bpos = bh % self.dim
                bsign = 1.0 if ((bh >> 4) & 1) == 0 else -1.0
                vec[bpos] += bsign * 1.5

        # L2 Normalization
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


local_embedder = LocalEmbedder()
