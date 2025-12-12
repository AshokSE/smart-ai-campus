# backend/services/qa_engine.py
import os
from dotenv import load_dotenv
load_dotenv()
from services.vector_store import query_similar_chunks
from services.embeddings import get_embeddings_for_chunks

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # default model

if not GROQ_API_KEY:
    print("[WARN] GROQ_API_KEY not set — generation will fail until set in .env")

def _build_prompt(context: str, question: str) -> str:
    prompt = f"""
You are a helpful and thorough assistant for a university student. Use ONLY the context below to answer the question.
If the context doesn't contain the answer, say "I don't have information about this in the provided documents."

CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
- Answer in clear, educational language.
- Provide a concise explanation and one example if applicable.
- If multiple relevant sources exist, synthesise them.
ANSWER:
"""
    return prompt

def _call_groq_chat(prompt: str) -> str:
    # Use the official groq client if installed, otherwise fallback to requests
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512
        )
        # depending on client version:
        content = resp.choices[0].message.content
        return content
    except Exception:
        # fallback via HTTP request (lightweight). If groq client not installed.
        import requests, json
        url = "https://api.groq.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        body = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512
        }
        r = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
        r.raise_for_status()
        j = r.json()
        # try to parse response
        return j["choices"][0]["message"]["content"]

def generate_answer_with_groq(question: str, top_k: int = 5) -> str:
    """
    High-level: embed question, fetch top-k chunks from Chroma, combine into context,
    call Groq to generate answer.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    # 1) Embed question
    q_embed = get_embeddings_for_chunks([question], use_cache=True, batch=False)[0]

    # 2) Query vector store
    matches = query_similar_chunks(q_embed, top_k=top_k)
    if not matches:
        return "I don't have information about this in the provided documents."

    # 3) Build context - keep within token/char budget (simple char-trim)
    context_lines = []
    total_chars = 0
    MAX_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "3000"))
    for m in matches:
        text = (m.metadata.get("text") if m.metadata else "") or ""
        if not text:
            continue
        if total_chars + len(text) > MAX_CHARS:
            remaining = MAX_CHARS - total_chars
            if remaining > 50:
                context_lines.append(text[:remaining])
            break
        context_lines.append(text)
        total_chars += len(text)

    context = "\n\n".join(context_lines)
    if not context.strip():
        return "I don't have information about this in the provided documents."

    # 4) build prompt and call Groq
    prompt = _build_prompt(context, question)
    try:
        answer = _call_groq_chat(prompt)
    except Exception as e:
        raise RuntimeError(f"Generation error: {e}")

    return answer.strip()
