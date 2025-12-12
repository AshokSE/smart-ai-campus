# backend/services/vector_store.py
import os
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "smart")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))

_client = None
_collection = None

def init_chroma():
    global _client, _collection
    if _client and _collection:
        return _collection
    try:
        import chromadb
        from chromadb.config import Settings
    except Exception as e:
        raise ImportError("chromadb is required. Install with: pip install chromadb") from e

    try:
        _client = chromadb.Client(Settings())
    except TypeError:
        _client = chromadb.Client()

    _collection = _client.get_or_create_collection(name=INDEX_NAME)
    print(f"[INFO] ChromaDB initialized (collection: {INDEX_NAME})")
    return _collection

def upsert_embeddings(vectors: List[Tuple[str, List[float], Dict[str, Any]]]) -> int:
    collection = init_chroma()
    if not vectors:
        print("[WARN] No vectors to upsert")
        return 0

    ids = [vid for vid, _, _ in vectors]
    embeddings = [vec for _, vec, _ in vectors]
    metadatas = [meta if isinstance(meta, dict) else {"text": str(meta)} for _, _, meta in vectors]
    documents = [meta.get("text") if isinstance(meta, dict) and meta.get("text") else "" for _, _, meta in vectors]

    res = collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)
    upserted = len(res.get("ids", ids)) if isinstance(res, dict) else len(ids)
    print(f"[INFO] Upserted {upserted} vectors into Chroma collection")
    return upserted

def store_embeddings(embeddings: List[List[float]], chunks: List[str]) -> int:
    if len(embeddings) != len(chunks):
        raise ValueError("Mismatch: embeddings count vs chunks count")
    vectors = [(f"chunk-{i}", emb, {"text": chunk}) for i, (emb, chunk) in enumerate(zip(embeddings, chunks))]
    return upsert_embeddings(vectors)

def query_embeddings(query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    collection = init_chroma()
    if len(query_vector) != EMBEDDING_DIMENSION:
        print(f"[WARN] Query vector dimension {len(query_vector)} != EMBEDDING_DIMENSION {EMBEDDING_DIMENSION}")

    resp = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["metadatas", "distances", "documents"]
    )

    ids = resp.get("ids", [[]])[0]
    metadatas = resp.get("metadatas", [[]])[0]
    distances = resp.get("distances", [[]])[0]

    results = []
    for i, _id in enumerate(ids):
        dist = distances[i] if i < len(distances) else None
        meta = metadatas[i] if i < len(metadatas) else {}
        score = None
        if dist is not None:
            try:
                score = 1.0 / (1.0 + float(dist))
            except Exception:
                score = None
        results.append({"id": _id, "score": score, "metadata": meta})
    print(f"[INFO] Query returned {len(results)} matches")
    return results

def query_similar_chunks(question_embedding: List[float], top_k: int = 5):
    rows = query_embeddings(question_embedding, top_k)
    class Match:
        def __init__(self, d):
            self.id = d.get("id")
            self.score = d.get("score")
            self.metadata = d.get("metadata")
    return [Match(r) for r in rows]

def clear_index() -> int:
    global _collection, _client
    col = init_chroma()
    try:
        count = _collection.count()
    except Exception:
        count = 0
    print(f"[WARN] Clearing collection '{INDEX_NAME}' with ~{count} vectors...")
    try:
        _client.delete_collection(name=INDEX_NAME)
    except Exception:
        try:
            _collection.delete()
        except Exception:
            pass
    _collection = _client.create_collection(name=INDEX_NAME)
    print("[INFO] Collection recreated successfully")
    return count

def get_or_create_index():
    return init_chroma()
