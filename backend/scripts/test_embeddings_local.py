#!/usr/bin/env python
"""Local test for `services.embeddings` using a fake OpenAI client.

This avoids needing a real OPENAI_API_KEY by setting a dummy env var
before importing the module, then monkeypatching `client.embeddings.create`.

Run with: python scripts/test_embeddings_local.py
"""
import os
import sys
from types import SimpleNamespace

# Ensure backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set a dummy OPENAI_API_KEY so `embeddings` module doesn't raise at import-time
os.environ.setdefault("OPENAI_API_KEY", "dummy_key_for_local_tests")

# Remove any previous cache for a clean test
from pathlib import Path
CACHE_FILE = Path(__file__).parent.parent / "services" / ".embeddings_cache.json"
if CACHE_FILE.exists():
    try:
        CACHE_FILE.unlink()
        print("Removed existing cache file for clean run.")
    except Exception as e:
        print("Warning: failed to remove cache file:", e)

# Import the module under test
import importlib
emb = importlib.import_module("services.embeddings")

# Replace the real client.embeddings.create with a fake
def fake_create(model, input):
    """Return a fake response object with predictable embeddings.

    Embedding vector: length-8 vector of floats = len(text)
    """
    if isinstance(input, list):
        data = [SimpleNamespace(embedding=[float(len(t))] * 8) for t in input]
    else:
        data = [SimpleNamespace(embedding=[float(len(input))] * 8)]
    return SimpleNamespace(data=data)

# Assign fake to the client's embeddings.create
try:
    emb.client.embeddings.create = fake_create
    print("Patched embeddings.client.embeddings.create with fake_create")
except Exception as e:
    print("Failed to patch client:", e)
    raise

# Prepare test chunks (including a duplicate to test cache)
chunks = [
    "The quick brown fox jumps over the lazy dog.",
    "Machine learning is a subset of artificial intelligence.",
    "Python is a versatile programming language.",
    "The quick brown fox jumps over the lazy dog.",  # duplicate
]

print("\nRunning get_embeddings_for_chunks (batch=True, use_cache=True)")
results = emb.get_embeddings_for_chunks(chunks, use_cache=True, batch=True)

print(f"Received {len(results)} embeddings")
print("Embedding[0] sample:", results[0][:4])

# Run again to trigger cache hits
print("\nRunning again to verify cache hits (should print 'Cache hit')")
results2 = emb.get_embeddings_for_chunks(chunks, use_cache=True, batch=True)

print(f"Received {len(results2)} embeddings on second run")

# Validate results are identical
same = all(r == s for r, s in zip(results, results2))
print("Embeddings identical across runs:", same)

# Check cache file created
print("\nCache file exists:", CACHE_FILE.exists())
if CACHE_FILE.exists():
    print("Cache file size:", CACHE_FILE.stat().st_size)
    with open(CACHE_FILE, 'r') as f:
        data = f.read(2000)
    print("Cache sample:", data[:400])

print("\nLocal embedding tests completed.")
