#!/usr/bin/env python
"""Live test for Pinecone integration using real keys from .env
This will upsert embeddings to your real Pinecone index and verify retrieval.

Run: python scripts/test_pinecone_live.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory
env_path = Path(__file__).parent.parent / ".env"
print(f"Loading env from: {env_path}")
if env_path.exists():
    load_dotenv(env_path)
    print("Loaded environment variables from .env")
else:
    print("Warning: .env file not found, using system environment")

# Verify keys are present
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "smart-campus-index")

if not PINECONE_KEY:
    print("ERROR: PINECONE_API_KEY not set in environment")
    sys.exit(1)
if not PINECONE_ENV:
    print("ERROR: PINECONE_ENVIRONMENT not set in environment")
    sys.exit(1)

print(f"\nUsing:")
print(f"  Index name: {INDEX_NAME}")
print(f"  Region: {PINECONE_ENV}")
print(f"  API key: {PINECONE_KEY[:20]}...{PINECONE_KEY[-10:]}")

# Import Pinecone (real client now)
try:
    from pinecone import Pinecone, ServerlessSpec
    print("\nImported real Pinecone client")
except Exception as e:
    print(f"ERROR: Failed to import Pinecone: {e}")
    sys.exit(1)

# Initialize Pinecone client
try:
    pc = Pinecone(api_key=PINECONE_KEY)
    print("Initialized Pinecone client")
except Exception as e:
    print(f"ERROR: Failed to initialize Pinecone: {e}")
    sys.exit(1)

# List existing indexes
try:
    indexes = pc.list_indexes().names()
    print(f"\nExisting indexes: {indexes}")
    if INDEX_NAME in indexes:
        print(f"✓ Index '{INDEX_NAME}' exists")
    else:
        print(f"✗ Index '{INDEX_NAME}' NOT found")
        print("Creating index...")
        try:
            pc.create_index(
                name=INDEX_NAME,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
            )
            print(f"Created index '{INDEX_NAME}'")
        except Exception as e:
            print(f"ERROR creating index: {e}")
except Exception as e:
    print(f"ERROR listing indexes: {e}")
    sys.exit(1)

# Get index
try:
    index = pc.Index(INDEX_NAME)
    print(f"Connected to index '{INDEX_NAME}'")
except Exception as e:
    print(f"ERROR: Failed to get index: {e}")
    sys.exit(1)

# Prepare test data
print("\n" + "="*60)
print("Upserting test embeddings...")
print("="*60)

test_chunks = [
    "Smart campus infrastructure uses IoT devices for monitoring.",
    "Machine learning models optimize energy consumption in buildings.",
    "Real-time data analytics improve student learning outcomes.",
    "Cloud computing provides scalable resources for educational systems.",
    "Cybersecurity protections ensure student data privacy.",
]

# Generate simple test embeddings (all dimension 768 for Gemini model)
test_embeddings = []
for i, chunk in enumerate(test_chunks):
    # Create a simple vector: hash-based for reproducibility
    vec = [float((hash(chunk + str(j)) % 100) / 100.0) for j in range(768)]
    test_embeddings.append(vec)

# Prepare vectors for upsert
vectors_to_upsert = []
for i, (chunk, emb) in enumerate(zip(test_chunks, test_embeddings)):
    vectors_to_upsert.append({
        "id": f"test-chunk-{i}",
        "values": emb,
        "metadata": {"text": chunk, "index": i}
    })

# Upsert to Pinecone
try:
    upsert_response = index.upsert(vectors=vectors_to_upsert)
    print(f"✓ Upserted {len(vectors_to_upsert)} vectors")
    print(f"  Response: {upsert_response}")
except Exception as e:
    print(f"✗ ERROR during upsert: {e}")
    sys.exit(1)

# Verify upsert by querying
print("\n" + "="*60)
print("Querying Pinecone to verify storage...")
print("="*60)

try:
    # Query with first embedding
    query_vec = test_embeddings[0]
    results = index.query(
        vector=query_vec,
        top_k=3,
        include_metadata=True
    )
    print(f"✓ Query returned {len(results.matches)} results")
    for i, match in enumerate(results.matches):
        print(f"  [{i+1}] id={match.id}, score={match.score:.4f}")
        if hasattr(match, 'metadata') and match.metadata:
            text = match.metadata.get('text', 'N/A')[:50]
            print(f"       text: {text}...")
except Exception as e:
    print(f"✗ ERROR during query: {e}")
    sys.exit(1)

# Index stats
print("\n" + "="*60)
print("Index statistics...")
print("="*60)

try:
    stats = index.describe_index_stats()
    print(f"✓ Index stats retrieved")
    print(f"  Total vectors: {stats.total_vector_count}")
    print(f"  Dimension: {stats.dimension}")
except Exception as e:
    print(f"✗ ERROR retrieving stats: {e}")

print("\n" + "="*60)
print("Live Pinecone test completed successfully!")
print("="*60)
