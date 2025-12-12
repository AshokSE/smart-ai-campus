#!/usr/bin/env python
"""Local test for `services.vector_store` using a fake Pinecone client.
This avoids talking to real Pinecone and avoids using your keys.

Run: python scripts/test_vector_store_local.py
"""
import os
import sys
import types
from types import SimpleNamespace

# Make sure project path is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load env from backend/.env (if present) so vector_store finds keys
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

# Insert a fake 'pinecone' module before importing services.vector_store
fake_pinecone = types.ModuleType('pinecone')

class FakeIndex:
    def __init__(self, name):
        self.name = name
        self._vectors = {}
    def upsert(self, vectors=None, **kwargs):
        # store by id
        for v in vectors or []:
            self._vectors[v['id']] = v
        return SimpleNamespace(upserted=len(self._vectors))
    def query(self, vector=None, top_k=5, include_metadata=False, **kwargs):
        matches = []
        # return up to top_k stored items
        for i, (vid, v) in enumerate(self._vectors.items()):
            if i >= top_k:
                break
            matches.append(SimpleNamespace(id=vid, score=1.0, metadata=v.get('metadata')))
        return SimpleNamespace(matches=matches)

class FakePineconeClient:
    def __init__(self, api_key=None):
        self._indexes = {}
    def list_indexes(self):
        # return object with names() method to match vector_store expectations
        return SimpleNamespace(names=lambda: list(self._indexes.keys()))
    def create_index(self, name, dimension=None, metric=None, spec=None):
        self._indexes[name] = {}
        return SimpleNamespace(created=True)
    def Index(self, name):
        idx = FakeIndex(name)
        # also keep a reference
        self._indexes[name] = idx
        return idx

class ServerlessSpec:
    def __init__(self, cloud=None, region=None):
        self.cloud = cloud
        self.region = region

fake_pinecone.Pinecone = FakePineconeClient
fake_pinecone.ServerlessSpec = ServerlessSpec

import importlib
sys.modules['pinecone'] = fake_pinecone

# Now import the vector_store module (it will import our fake pinecone)
try:
    vs = importlib.import_module('services.vector_store')
    print('Imported services.vector_store with fake Pinecone')
except Exception as e:
    print('Failed to import services.vector_store:', e)
    raise

# Prepare test embeddings and chunks
chunks = [
    'Chunk one text content',
    'Chunk two different text',
    'Chunk three final text',
]
# Use small vectors for test
embeddings = [[float(len(c))] * 8 for c in chunks]

# Call store_embeddings
print('\nCalling store_embeddings...')
vs.store_embeddings(embeddings, chunks)

# Inspect the fake index stored vectors
idx = vs.index
try:
    stored = idx._vectors
    print(f'Vectors stored count: {len(stored)}')
    # Verify metadata matches
    ok = True
    for i, chunk in enumerate(chunks):
        vid = f'chunk-{i}'
        if vid not in stored:
            print(f'Missing id: {vid}')
            ok = False
        else:
            meta = stored[vid].get('metadata', {})
            if meta.get('text') != chunk:
                print(f'Metadata mismatch for {vid}:', meta)
                ok = False
    print('Metadata verification:', 'PASS' if ok else 'FAIL')
except Exception as e:
    print('Failed to inspect fake index:', e)

# Test query_similar_chunks
print('\nTesting query_similar_chunks...')
q_results = vs.query_similar_chunks([1.0]*8, top_k=2)
print('Query returned matches count:', len(q_results))
for m in q_results:
    print('  id:', m.id, 'metadata text:', m.metadata.get('text'))

print('\nLocal vector store test completed.')
