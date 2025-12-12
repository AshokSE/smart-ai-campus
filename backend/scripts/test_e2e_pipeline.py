#!/usr/bin/env python3
"""
End-to-end test of the Smart Campus backend pipeline.
Tests: PDF upload → chunking → embeddings → Pinecone → QA
"""

import requests
import json
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

# Create test PDF
def create_test_pdf():
    """Create a simple test PDF with sample content."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from io import BytesIO
        
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        
        # Add sample text
        c.drawString(100, 750, "Python Programming Guide")
        c.drawString(100, 720, "Chapter 1: Introduction to Python")
        c.drawString(100, 690, "")
        c.drawString(100, 670, "Python is a high-level programming language known for its simplicity and readability.")
        c.drawString(100, 650, "It was created by Guido van Rossum and first released in 1991.")
        c.drawString(100, 630, "")
        c.drawString(100, 610, "Key Features:")
        c.drawString(100, 590, "- Easy to learn and read")
        c.drawString(100, 570, "- Dynamic typing")
        c.drawString(100, 550, "- Automatic memory management")
        c.drawString(100, 530, "- Extensive standard library")
        c.drawString(100, 510, "")
        c.drawString(100, 490, "Python is widely used in web development, data science, machine learning, and automation.")
        c.drawString(100, 470, "It has a large and active community with thousands of packages available on PyPI.")
        
        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer
    except ImportError:
        print("reportlab not installed. Skipping PDF creation.")
        return None

def test_pipeline():
    """Test the complete pipeline."""
    print("=" * 80)
    print("SMART CAMPUS BACKEND E2E TEST")
    print("=" * 80)
    
    # Test 1: Health check
    print("\n[1] Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed:", response.json())
        else:
            print("❌ Health check failed:", response.status_code)
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test 2: Ping
    print("\n[2] Testing ping endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/ping")
        if response.status_code == 200:
            print("✅ Ping passed:", response.json())
        else:
            print("❌ Ping failed:", response.status_code)
    except Exception as e:
        print(f"❌ Ping error: {e}")
    
    # Test 3: Chunk text
    print("\n[3] Testing chunk endpoint...")
    try:
        chunk_payload = {
            "text": "This is a test document. It contains multiple sentences. Each sentence should be processed separately or together depending on the chunking method.",
            "chunk_size": 30,
            "overlap": 5,
            "method": "word"
        }
        response = requests.post(f"{BASE_URL}/process-chunks", json=chunk_payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chunking passed. Created {result.get('chunks_count', 0)} chunks")
            print(f"   Chunks: {result.get('chunks', [])[:2]}")
        else:
            print(f"❌ Chunking failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Chunking error: {e}")
    
    # Test 4: Process PDF (if we can create one)
    print("\n[4] Testing PDF upload endpoint...")
    pdf = create_test_pdf()
    if pdf:
        try:
            files = {"file": ("test.pdf", pdf, "application/pdf")}
            response = requests.post(f"{BASE_URL}/process-pdf-full", files=files)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ PDF processing passed!")
                print(f"   Chunks: {result.get('chunks_count', 0)}")
                print(f"   Embeddings: {result.get('embeddings_count', 0)}")
                print(f"   Vectors stored: {result.get('vectors_stored', 0)}")
                
                # Test 5: Query
                if result.get('vectors_stored', 0) > 0:
                    print("\n[5] Testing query endpoint...")
                    try:
                        query_payload = {"query": "What is Python?", "top_k": 3}
                        response = requests.post(f"{BASE_URL}/query", json=query_payload)
                        if response.status_code == 200:
                            query_result = response.json()
                            print(f"✅ Query passed!")
                            print(f"   Results found: {len(query_result.get('results', []))}")
                            for i, result_item in enumerate(query_result.get('results', [])[:2], 1):
                                print(f"   {i}. Score: {result_item.get('score', 'N/A')}")
                                print(f"      Text: {result_item.get('text', 'N/A')[:60]}...")
                        else:
                            print(f"❌ Query failed: {response.status_code}")
                            print(f"   Error: {response.text}")
                    except Exception as e:
                        print(f"❌ Query error: {e}")
                    
                    # Test 6: Get answer
                    print("\n[6] Testing answer endpoint...")
                    try:
                        answer_payload = {"query": "What is Python?", "top_k": 3}
                        response = requests.post(f"{BASE_URL}/answer", json=answer_payload)
                        if response.status_code == 200:
                            answer_result = response.json()
                            print(f"✅ Answer generation passed!")
                            print(f"   Answer: {answer_result.get('answer', 'N/A')[:100]}...")
                            if answer_result.get('sources'):
                                print(f"   Sources used: {len(answer_result.get('sources', []))}")
                        else:
                            print(f"❌ Answer failed: {response.status_code}")
                            print(f"   Error: {response.text}")
                    except Exception as e:
                        print(f"❌ Answer error: {e}")
            else:
                print(f"❌ PDF processing failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ PDF processing error: {e}")
    else:
        print("⚠️  Skipping PDF test (reportlab not available)")
    
    print("\n" + "=" * 80)
    print("E2E TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_pipeline()
