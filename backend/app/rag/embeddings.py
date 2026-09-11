import os
import logging
from typing import List, Optional
import numpy as np

from backend.app.config import settings

logger = logging.getLogger("agni.rag.embeddings")

EMBEDDING_DIM = getattr(settings, "EMBEDDING_DIM", 384)
DEFAULT_MODEL_NAME = getattr(settings, "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


class LocalEmbedder:
    """Sovereign local semantic embedding engine using sentence-transformers/all-MiniLM-L6-v2.
    
    100% offline CPU inference using local pre-cached model weights.
    Produces 384-dimensional L2-normalized dense vectors for cosine similarity retrieval.
    Zero runtime network calls or external API dependencies.
    """

    def __init__(self, model_name: Optional[str] = None, dim: int = EMBEDDING_DIM):
        self.model_name = model_name or os.environ.get("EMBEDDING_MODEL_PATH") or DEFAULT_MODEL_NAME
        self.dim = dim
        self._model = None

    def _resolve_model_path(self, target: str) -> str:
        """Prefers verified local snapshot directory on disk to guarantee zero network resolution."""
        if os.path.isdir(target):
            return target

        # Check standard HuggingFace hub cache snapshots for all-MiniLM-L6-v2
        if "all-MiniLM-L6-v2" in target:
            from pathlib import Path
            hf_cache_snapshot = (
                Path.home()
                / ".cache"
                / "huggingface"
                / "hub"
                / "models--sentence-transformers--all-MiniLM-L6-v2"
                / "snapshots"
            )
            if hf_cache_snapshot.is_dir():
                snapshots = [str(p) for p in hf_cache_snapshot.iterdir() if p.is_dir()]
                if snapshots:
                    # Use direct verified filesystem snapshot path
                    logger.info(f"Using direct local model snapshot path: {snapshots[0]}")
                    return snapshots[0]
        return target

    def _get_model(self):
        if self._model is None:
            # Enforce offline air-gapped operation
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"
            
            resolved_path = self._resolve_model_path(self.model_name)
            try:
                from sentence_transformers import SentenceTransformer
                # Load strictly from local cache/filesystem; forbid runtime downloads
                self._model = SentenceTransformer(resolved_path, local_files_only=True)
                logger.info(f"Loaded local semantic embedding model from: '{resolved_path}' (dim={self.dim})")
            except Exception as e:
                err_msg = (
                    f"Failed to load local semantic embedding model '{self.model_name}'. "
                    f"In sovereign air-gapped mode, automatic remote downloading at runtime is strictly disabled. "
                    f"Please ensure the model weights are pre-cached in the local HuggingFace cache "
                    f"or configured via EMBEDDING_MODEL_PATH. Original error: {e}"
                )
                logger.error(err_msg)
                raise RuntimeError(err_msg) from e
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """Embeds a single string into a 384-dimensional normalized dense vector."""
        if not text or not text.strip():
            return [0.0] * self.dim
        model = self._get_model()
        vec = model.encode(text, normalize_embeddings=True, convert_to_numpy=True)
        return vec.tolist() if hasattr(vec, "tolist") else list(vec)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of strings into normalized dense vectors."""
        if not texts:
            return []
        model = self._get_model()
        cleaned = [t if t and t.strip() else "" for t in texts]
        vecs = model.encode(cleaned, normalize_embeddings=True, convert_to_numpy=True)
        return vecs.tolist() if hasattr(vecs, "tolist") else [list(v) for v in vecs]


local_embedder = LocalEmbedder()
