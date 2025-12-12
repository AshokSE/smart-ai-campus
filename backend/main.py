from pydantic import BaseModel, EmailStr

# ----------------- USER MODELS -----------------
class SignupModel(BaseModel):
    fullName: str
    email: EmailStr
    password: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

# ----------------- MYSQL SETUP -----------------
from services.database import db, cursor

# ----------------- AUTH UTILS -----------------
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ----------------- FASTAPI SETUP -----------------
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

# Import services
from services.pdf_reader import extract_text_from_pdf, chunk_text
from services.embeddings import get_embeddings_for_chunks
from services.vector_store import store_embeddings, query_similar_chunks, clear_index, get_or_create_index
from services.qa_engine import generate_answer_with_groq

app = FastAPI(title="Smart Campus API (Groq + Chroma)", version="1.3.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- ROUTE MODELS -----------------
class ChunkRequest(BaseModel):
    text: str
    chunk_size: int = 512
    overlap: int = 50
    method: str = "word"

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


# ============================================================
#                AUTH ROUTES (LOGIN + SIGNUP)
# ============================================================

@app.post("/signup")
def signup(data: SignupModel):
    # Check if email exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
    existing = cursor.fetchone()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = hash_password(data.password)

    # Insert new user
    cursor.execute(
        "INSERT INTO users (fullName, email, password) VALUES (%s, %s, %s)",
        (data.fullName, data.email, hashed_pw)
    )
    db.commit()

    return {
        "status": "success",
        "message": "User registered successfully"
    }


@app.post("/login")
def login(data: LoginModel):
    # Fetch user
    cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Check password
    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "status": "success",
        "message": "Login successful",
        "user_id": user["id"],
        "fullName": user["fullName"]
    }


# ============================================================
#                       PDF / VECTOR / QUIZ
#             (These parts are untouched)
# ============================================================

@app.get("/")
def home():
    return {"message": "FastAPI server running ✅"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_and_process_pdf(file: UploadFile = File(...), chunk_size: int = 512, overlap: int = 50):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    pdf_bytes = await file.read()
    text = extract_text_from_pdf(pdf_bytes)

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from PDF")

    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap, method="word")
    embeddings = get_embeddings_for_chunks(chunks, use_cache=True, batch=True)
    saved = store_embeddings(embeddings, chunks)

    return {
        "filename": file.filename,
        "text_length": len(text),
        "chunks_created": len(chunks),
        "vectors_stored": saved,
        "status": "success"
    }


@app.post("/query")
async def query_endpoint(req: QueryRequest):
    qvec = get_embeddings_for_chunks([req.query], use_cache=True, batch=False)[0]
    matches = query_similar_chunks(qvec, top_k=req.top_k)

    formatted = []
    for i, m in enumerate(matches):
        formatted.append({
            "rank": i + 1,
            "id": m.id,
            "score": m.score,
            "text": m.metadata.get("text") if m.metadata else ""
        })

    return {"query": req.query, "results_count": len(formatted), "results": formatted}


@app.post("/answer")
async def answer_endpoint(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    answer = generate_answer_with_groq(req.query, top_k=req.top_k)
    return {"question": req.query, "answer": answer}


@app.post("/clear-index")
def clear_index_route():
    count = clear_index()
    return {"status": "success", "cleared_count_approx": count}


@app.get("/vector-count")
def vector_count_route():
    col = get_or_create_index()
    return {"count": col.count()}


@app.post("/generate-quiz")
async def generate_quiz(topic: str = Form(...), file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    text = extract_text_from_pdf(pdf_bytes)

    if not text.strip():
        raise HTTPException(400, "PDF has no readable text")

    limited_text = text[:2500]

    prompt = f"""
You MUST return ONLY valid JSON.

Create 5 MCQs based on the topic and PDF.

USER TOPIC: "{topic}"

PDF CONTENT:
{limited_text}
"""

    quiz_text = generate_answer_with_groq(prompt)

    import re
    match = re.search(r"\[.*\]", quiz_text, re.DOTALL)
    quizzes = None

    if match:
        try:
            quizzes = json.loads(match.group(0))
        except:
            quizzes = None

    if quizzes is None:
        quizzes = [{"raw_output": quiz_text}]

    return {
        "filename": file.filename,
        "topic": topic,
        "quiz_count": len(quizzes) if isinstance(quizzes, list) else 0,
        "quizzes": quizzes,
        "status": "success"
    }


# ============================================================
#                       SERVER RUN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
