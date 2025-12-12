# Quick Start Testing Guide

## Prerequisites
- Python 3.13 (Backend venv already configured)
- Node.js & npm installed
- `.env` file configured with API keys

---

## Running Backend

```powershell
cd d:\smart-ai-campus\backend
D:/smart-ai-campus/backend/venv/Scripts/python.exe main.py
```

**Expected Output:**
```
[INFO] Starting Smart Campus Backend...
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Verify Backend:**
- Open browser: http://localhost:8000/health
- Should return: `{"status": "healthy", "service": "smart-campus-backend"}`
- API docs: http://localhost:8000/docs

---

## Running Frontend

```powershell
cd d:\smart-ai-campus\frontend\my-app
npm start
```

**Expected Output:**
```
Compiled successfully!
You can now view my-app in the browser.
  Local:            http://localhost:3000
```

**Frontend will open automatically at:** http://localhost:3000

---

## Testing the Full Integration

### Test 1: API Health Check
```powershell
# In PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

**Expected Response:**
```json
{
    "status": "healthy",
    "service": "smart-campus-backend"
}
```

### Test 2: PDF Upload
1. Go to http://localhost:3000
2. Drag and drop a PDF file
3. Should see: "Uploaded! Text length: [count] chars. Status: success"

### Test 3: Ask a Question
1. After uploading, type a question in the "Ask a question" box
2. Click "Ask"
3. Should see answer generated in the Result Box

---

## Troubleshooting

### Frontend won't connect to backend
- **Cause:** Backend not running
- **Fix:** Start backend first on port 8000

### "No answer returned from server"
- **Cause:** Pinecone index not configured or PDF not processed
- **Fix:** 
  1. Check `.env` has valid PINECONE_API_KEY
  2. Use `/process-pdf-full` endpoint to store embeddings first

### Port already in use
```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000 | Get-Process

# Find process using port 3000
Get-NetTCPConnection -LocalPort 3000 | Get-Process
```

---

## Files to Monitor

### Backend
- `backend/main.py` - API server
- `backend/services/*.py` - Core services
- `backend/.env` - Configuration (required)

### Frontend
- `frontend/my-app/src/*.jsx` - React components
- `frontend/my-app/src/api.jsx` - Backend communication

---

## API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/health` | GET | Detailed health info |
| `/upload` | POST | Upload and extract PDF |
| `/process-pdf-full` | POST | Full pipeline: extract → chunk → embed → store |
| `/process-chunks` | POST | Chunk text with custom parameters |
| `/query` | POST | Search embeddings in Pinecone |
| `/answer` | POST | Ask question and get answer |
| `/docs` | GET | Interactive API documentation |

---

## Environment Variables Needed

```env
# Embeddings Model
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Pinecone Vector Store
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=your_env_here
PINECONE_INDEX_NAME=smart-campus-index

# Generation Model
HF_GENERATION_MODEL=google/flan-t5-base

# Optional
EMBEDDING_BATCH_SIZE=100
MAX_CONTEXT_LENGTH=3000
```

---

## Next Steps

1. ✓ Ensure `.env` is properly configured
2. Run backend server
3. Run frontend app
4. Test with sample PDF
5. Verify Q&A workflow
6. Check console for any errors
