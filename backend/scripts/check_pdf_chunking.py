#!/usr/bin/env python
"""Test script to create a PDF, extract text with PyMuPDF (fitz), and verify
that a character-level chunker preserves every character.

Run: python scripts/check_pdf_chunking.py
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services import pdf_reader
import fitz

PDF_DIR = os.path.join(os.path.dirname(__file__), "tmp")
PDF_PATH = os.path.join(PDF_DIR, "test_chunk.pdf")

SAMPLE_TEXT = (
    "Line1: ABC 123\n"
    "Line2: Unicode 你好! ☺\n"
    "Line3: Tabs\tand multiple   spaces\n"
    "Line4: Punctuation .,!?:;\n"
    "Line5: Zero-width\u200b and other control chars: \u200b"
)


def make_sample_pdf(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc = fitz.open()
    page = doc.new_page()
    rect = fitz.Rect(72, 72, 540, 720)
    page.insert_textbox(rect, text, fontsize=11)
    doc.save(path)
    doc.close()


def extract_text_from_pdf(path: str) -> str:
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def chunk_chars(text: str, chunk_size: int = 1, overlap: int = 0):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be >= 1")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >=0 and < chunk_size")
    chunks = []
    i = 0
    step = chunk_size - overlap
    while i < len(text):
        chunks.append(text[i : i + chunk_size])
        i += step
    return chunks


def main():
    print("=== PDF Chunking Test ===\n")
    print("Creating sample PDF:", PDF_PATH)
    make_sample_pdf(PDF_PATH, SAMPLE_TEXT)

    print("Extracting text from PDF...")
    extracted = extract_text_from_pdf(PDF_PATH)
    print("Extracted length:", len(extracted))
    print("Extracted sample (first 100 chars):\n", repr(extracted[:100]))
    print()

    # Test 1: Internal per-character chunking
    print("Test 1: Internal per-character chunking")
    chunks = chunk_chars(extracted, chunk_size=1, overlap=0)
    reconstructed = "".join(chunks)
    print(f"  Number of character chunks: {len(chunks)}")
    print(f"  Reconstructed length: {len(reconstructed)}")
    print(f"  {'PASS' if reconstructed == extracted else 'FAIL'}")
    print(f"  First 40 character chunks: {chunks[:40]}")
    print()

    # Test 2: Using pdf_reader.chunk_text_per_char()
    print("Test 2: pdf_reader.chunk_text_per_char()")
    chunks_from_module = pdf_reader.chunk_text_per_char(extracted)
    reconstructed2 = "".join(chunks_from_module)
    print(f"  Number of character chunks: {len(chunks_from_module)}")
    print(f"  Reconstructed length: {len(reconstructed2)}")
    print(f"  {'PASS' if reconstructed2 == extracted else 'FAIL'}")
    print()

    # Test 3: Per-character chunking with overlap
    print("Test 3: Per-character chunking with overlap=1")
    sample_text = "ABCDE"
    chunks_overlap = pdf_reader.chunk_text(sample_text, chunk_size=2, overlap=1, method="char")
    print(f"  Input: {sample_text!r}")
    print(f"  Chunks: {chunks_overlap}")
    expected = ["AB", "BC", "CD", "DE"]
    print(f"  Expected: {expected}")
    print(f"  {'PASS' if chunks_overlap == expected else 'FAIL'}")
    print()

    # Test 4: Word-based chunking
    print("Test 4: Word-based chunking")
    sample_text_words = "This is a test sentence for word chunking"
    chunks_words = pdf_reader.chunk_text(sample_text_words, chunk_size=2, overlap=1, method="word")
    print(f"  Input: {sample_text_words!r}")
    print(f"  Chunks (chunk_size=2, overlap=1): {chunks_words}")
    print()

    # Test 5: Verify no character loss with pdf_reader
    print("Test 5: Character preservation with pdf_reader.chunk_text()")
    all_chars_per_char = pdf_reader.chunk_text(extracted, chunk_size=1, overlap=0, method="char")
    reconstructed_char = "".join(all_chars_per_char)
    print(f"  Characters in original: {len(extracted)}")
    print(f"  Characters reconstructed: {len(reconstructed_char)}")
    print(f"  {'PASS: Every character preserved' if reconstructed_char == extracted else 'FAIL: Character loss detected'}")
    print()

    print("=== Summary ===")
    print("All tests completed. See results above.")


if __name__ == "__main__":
    main()

