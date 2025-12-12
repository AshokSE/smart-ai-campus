# backend/services/embeddings.py
from typing import List, Dict, Any
import os
import hashlib
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

HF_EMBEDDING_MODEL = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "100"))
CACHE_FILE = Path(__file__).parent / ".embeddings_cache.json"

_model = None

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print(f"[INFO] Loading embedding model: {HF_EMBEDDING_MODEL}")
        _model = SentenceTransformer(HF_EMBEDDING_MODEL)
    return _model

def _load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load cache: {e}")
    return {}

def _save_cache(cache):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"[WARN] Failed to save cache: {e}")

def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_embedding(text: str, use_cache: bool = True) -> List[float]:
    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty text")
    model = _get_model()
    cache = _load_cache() if use_cache else {}
    key = _hash_text(text)
    if use_cache and key in cache:
        return cache[key]
    vec = model.encode(text).tolist()
    if use_cache:
        cache[key] = vec
        _save_cache(cache)
    return vec

def get_embeddings_batch(texts: List[str], use_cache: bool = True) -> List[List[float]]:
    if not texts:
        return []
    model = _get_model()
    cache = _load_cache() if use_cache else {}
    results = [None] * len(texts)
    uncached_texts = []
    uncached_indices = []
    for i, t in enumerate(texts):
        if not t or not t.strip():
            raise ValueError(f"Text at index {i} is empty")
        key = _hash_text(t)
        if use_cache and key in cache:
            results[i] = cache[key]
        else:
            uncached_texts.append(t)
            uncached_indices.append(i)
    for start in range(0, len(uncached_texts), EMBEDDING_BATCH_SIZE):
        end = start + EMBEDDING_BATCH_SIZE
        batch = uncached_texts[start:end]
        vecs = model.encode(batch)
        for j, vec in enumerate(vecs):
            idx = uncached_indices[start + j]
            arr = vec.tolist()
            results[idx] = arr
            if use_cache:
                cache[_hash_text(batch[j])] = arr
    if use_cache:
        _save_cache(cache)
    return results

def get_embeddings_for_chunks(chunks: List[str], use_cache: bool = True, batch: bool = True) -> List[List[float]]:
    if not chunks:
        raise ValueError("No chunks provided")
    if batch:
        return get_embeddings_batch(chunks, use_cache=use_cache)
    else:
        return [get_embedding(c, use_cache=use_cache) for c in chunks]
