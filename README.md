# Smart AI Campus Assistant 🤖📚

A comprehensive AI-powered campus management system that revolutionizes how students and faculty interact with course materials through intelligent document processing, semantic search, and automated quiz generation.

## 🌟 Features

- **📄 PDF Processing**: Advanced text extraction and intelligent chunking from PDF documents
- **🧠 AI Embeddings**: Generate semantic embeddings using Google Generative AI (Gemini)
- **🔍 Vector Search**: Store and query embeddings with Pinecone vector database
- **💬 Intelligent QA**: Answer questions using context from uploaded documents with source citations
- **📝 Quiz Generation**: Automatically generate quizzes from document content
- **🔐 User Authentication**: Secure signup/login system with password hashing
- **🎨 Modern UI**: Responsive React frontend with smooth animations and 3D effects
- **⚡ FastAPI Backend**: High-performance REST API with automatic documentation

## 🛠️ Tech Stack

### Backend
- **Python 3.13+** - Core language
- **FastAPI** - Modern web framework
- **PyMuPDF** - PDF text extraction
- **Google Generative AI** - Embeddings and LLM (Gemini)
- **Pinecone** - Vector database
- **MySQL** - User data storage
- **bcrypt** - Password hashing
- **Uvicorn** - ASGI server

### Frontend
- **React 19** - UI framework
- **Axios** - HTTP client
- **React Router** - Navigation
- **GSAP** - Animations
- **Three.js** - 3D graphics
- **React Dropzone** - File uploads

## 📁 Project Structure

```
smart-ai-campus/
├── backend/
│   ├── main.py                    # FastAPI application with all routes
│   ├── .env                       # Environment variables (API keys)
│   ├── .env.example               # Environment template
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py                # Authentication utilities
│   │   ├── database.py            # MySQL database connection
│   │   ├── embeddings.py          # Google AI embeddings service
│   │   ├── models.py              # Pydantic data models
│   │   ├── pdf_reader.py          # PDF processing and chunking
│   │   ├── qa_engine.py           # Question answering with Gemini
│   │   └── vector_store.py        # Pinecone vector operations
│   ├── scripts/
│   │   ├── check_pdf_chunking.py
│   │   ├── run_e2e_test.py
│   │   ├── test_backend_system.py
│   │   ├── test_e2e_pipeline.py
│   │   ├── test_embeddings_local.py
│   │   ├── test_embeddings.py
│   │   ├── test_pinecone_live.py
│   │   └── test_vector_store_local.py
│   └── venv/                      # Python virtual environment
├── frontend/
│   └── my-app/
│       ├── public/
│       │   ├── index.html
│       │   ├── manifest.json
│       │   └── robots.txt
│       ├── src/
│       │   ├── api.jsx            # API integration functions
│       │   ├── App.js             # Main React application
│       │   ├── index.js           # React entry point
│       │   ├── components/
│       │   │   ├── AskBox.jsx     # Question input component
│       │   │   ├── ClickSpark.jsx # Animation effects
│       │   │   ├── FloatingLines.jsx # Background animations
│       │   │   ├── LoginPage.jsx  # User login interface
│       │   │   ├── QuizBox.jsx    # Quiz display component
│       │   │   ├── ResultBox.jsx  # Answer display component
│       │   │   ├── Signup.jsx     # User registration
│       │   │   ├── TextType.jsx   # Typing animation
│       │   │   └── UploadBox.jsx  # File upload interface
│       │   └── setupTests.js
│       ├── package.json
│       └── README.md
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.13+** - Backend runtime
- **Node.js 16+** - Frontend build tools
- **MySQL** - Database server
- **Git** - Version control

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment** (if not exists)
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install fastapi uvicorn pymupdf google-generativeai pinecone-client mysql-connector-python bcrypt python-multipart
   ```

5. **Configure environment variables**
   Create `.env` file in `backend/` directory:
   ```env
   # AI Service Keys
   GEMINI_API_KEY=your_gemini_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here

   # Database Configuration
   DB_HOST=localhost
   DB_USER=your_mysql_username
   DB_PASSWORD=your_mysql_password
   DB_NAME=smart_campus_db

   # Optional Pinecone Settings
   PINECONE_ENVIRONMENT=us-west1
   PINECONE_INDEX_NAME=smart-campus-index
   ```

6. **Start the backend server**
   ```bash
   # Option 1: Using uvicorn
   uvicorn main:app --reload --host 127.0.0.1 --port 8000

   # Option 2: Direct Python execution
   python main.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend/my-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Environment Variables

### Required
- `GEMINI_API_KEY` - Google AI Studio API key for embeddings and QA
- `PINECONE_API_KEY` - Pinecone vector database API key
- `DB_HOST` - MySQL database host
- `DB_USER` - MySQL database username
- `DB_PASSWORD` - MySQL database password
- `DB_NAME` - MySQL database name

### Optional
- `PINECONE_ENVIRONMENT` - Pinecone region (default: us-west1)
- `PINECONE_INDEX_NAME` - Pinecone index name (default: smart-campus-index)

## 📡 API Endpoints

### Authentication
- `POST /signup` - User registration
  ```json
  {
    "fullName": "John Doe",
    "email": "john@example.com",
    "password": "securepassword"
  }
  ```

- `POST /login` - User authentication
  ```json
  {
    "email": "john@example.com",
    "password": "securepassword"
  }
  ```

### Document Processing
- `POST /upload` - Upload and process PDF documents
  - Accepts multipart/form-data with PDF file
  - Returns extracted text and processing status

### Question Answering
- `POST /answer` - Generate answers from document context
  ```json
  {
    "query": "What is machine learning?",
    "top_k": 3
  }
  ```

### Quiz Generation
- `POST /generate-quiz` - Create quizzes from uploaded content
  ```json
  {
    "topic": "Machine Learning",
    "difficulty": "intermediate",
    "num_questions": 5
  }
  ```

### System Health
- `GET /` - API information
- `GET /health` - Health check endpoint

## 🧪 Testing

### Backend Tests
```bash
cd backend

# System verification
python scripts/test_backend_system.py

# End-to-end pipeline test
python scripts/test_e2e_pipeline.py

# Individual service tests
python scripts/test_embeddings.py
python scripts/test_pinecone_live.py
```

### Frontend Tests
```bash
cd frontend/my-app
npm test
```

## 🔒 Security Features

- **Password Hashing**: bcrypt for secure password storage
- **CORS Protection**: Configured for localhost:3000
- **Input Validation**: Pydantic models for request validation
- **API Key Protection**: Sensitive keys stored in environment variables
- **File Type Validation**: PDF-only uploads with size limits

## 🚦 Performance Optimizations

- **Embedding Caching**: Prevents duplicate API calls for same content
- **Batch Processing**: Efficient embedding generation in batches
- **Lazy Initialization**: Services initialize only when needed
- **Vector Indexing**: Fast approximate nearest neighbor search
- **Context Truncation**: Prevents token limit issues in QA

## 🐛 Troubleshooting

### Common Issues

**1. "GEMINI_API_KEY not found"**
- Verify `.env` file exists in `backend/` directory
- Check key format and spelling
- Ensure file is not missing or corrupted

**2. "Pinecone connection failed"**
- Verify internet connection
- Check `PINECONE_API_KEY` is valid
- Verify index exists in Pinecone console
- Check region matches `PINECONE_ENVIRONMENT`

**3. "PDF processing error"**
- Ensure file is valid PDF
- Check file size (max recommended: 100MB)
- Verify PDF contains text (not image-only)

**4. "Rate limit exceeded"**
- Wait a few minutes before trying again
- Check API quota in respective console
- Consider upgrading to paid tier

### Debug Mode

Enable debug output:
```bash
# Set Python logging to DEBUG
export PYTHONUNBUFFERED=1
uvicorn main:app --reload --log-level debug
```

---

## 📈 Roadmap

### Phase 1: Core Features ✅
- PDF processing and chunking
- AI embeddings and vector search
- Question answering system
- User authentication
- Quiz generation
- React frontend

### Phase 2: Enhancement (Next)
- Advanced search filters
- Conversation history
- Multi-language support
- Mobile responsiveness

### Phase 3: Scale (Future)
- Collaborative features
- Admin dashboard
- Analytics and insights
- Mobile app

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Generative AI** - For Gemini LLM and embeddings
- **Pinecone** - Vector database infrastructure
- **PyMuPDF** - PDF processing capabilities
- **FastAPI** - Modern Python web framework
- **React** - Frontend UI framework

---

**Built with ❤️ for smarter campus learning experiences**

*Last Updated: December 12, 2025*
