# backend/services/pdf_reader.py
import fitz

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    for page in pdf:
        page_text = page.get_text("text")
        text += page_text + "\n"
    pdf.close()
    cleaned_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    return cleaned_text

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50, method: str = "word"):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("0 <= overlap < chunk_size required")
    if method == "char":
        chunks = []
        step = chunk_size - overlap
        i = 0
        while i + chunk_size <= len(text):
            chunks.append(text[i:i+chunk_size])
            i += step
        if len(chunks) == 0 and len(text) > 0:
            chunks.append(text)
        return chunks
    elif method == "word":
        words = text.split()
        if not words:
            return []
        chunks = []
        step = max(1, chunk_size - overlap)
        i = 0
        while i < len(words):
            end = min(i + chunk_size, len(words))
            chunk_words = words[i:end]
            chunks.append(" ".join(chunk_words))
            i += step
            if i >= len(words):
                break
        return chunks
    else:
        raise ValueError("method must be 'char' or 'word'")

def chunk_text_per_char(text: str):
    return chunk_text(text, chunk_size=1, overlap=0, method="char")
