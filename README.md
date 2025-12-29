# Medical CDSS - Complete File Structure & Setup

## 📁 Complete Directory Structure

```
medical-cdss/
│
├── backend/
│   ├── __init__.py                 # Empty file (makes it a Python package)
│   ├── main.py                     # FastAPI application (ARTIFACT 1)
│   ├── models.py                   # Pydantic models (included in ARTIFACT 1)
│   ├── database.py                 # SQLAlchemy database (included in ARTIFACT 1)
│   ├── auth.py                     # Authentication utilities (ARTIFACT 6)
│   ├── ml_inference.py             # ML model inference (included in ARTIFACT 1)
│   ├── report_generator.py         # PDF report generation (included in ARTIFACT 1)
│   └── requirements.txt            # Python dependencies
│
├── frontend/
│   ├── index.html                  # Login page (ARTIFACT 4 - section 1)
│   ├── dashboard.html              # Dashboard page (ARTIFACT 4 - section 2)
│   ├── analysis.html               # Analysis page (ARTIFACT 4 - section 3)
│   ├── records.html                # Records page (ARTIFACT 4 - section 4)
│   │
│   ├── css/
│   │   └── styles.css              # All styles (ARTIFACT 2)
│   │
│   └── js/
│       ├── auth.js                 # Authentication JS (ARTIFACT 3 - complete)
│       ├── dashboard.js            # Dashboard JS (ARTIFACT 3 - complete)
│       ├── analysis.js             # Analysis JS (ARTIFACT 3 - complete)
│       └── records.js              # Records JS (ARTIFACT 3 - complete)
│
├── models/
│   └── pneumonia_model.pkl         # YOUR TRAINED MODEL (from Google Colab)
│
├── uploads/                        # Auto-created (temporary image storage)
│
├── reports/                        # Auto-created (generated PDF reports)
│
├── medical_cdss.db                 # Auto-created (SQLite database)
│
├── .gitignore                      # Git ignore file
├── README.md                       # Project documentation
└── setup.sh                        # Quick setup script (below)
```

---

## 🚀 Quick Setup Script

### For Linux/Mac (setup.sh)

```bash
#!/bin/bash

# Medical CDSS Quick Setup Script
# Save this as: setup.sh
# Make executable: chmod +x setup.sh
# Run: ./setup.sh

echo "🏥 Medical CDSS - Quick Setup"
echo "=============================="
echo ""

# Create project structure
echo "📁 Creating project directories..."
mkdir -p backend frontend/css frontend/js models uploads reports

# Create __init__.py
touch backend/__init__.py

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn python-multipart sqlalchemy pydantic python-jose passlib bcrypt PyJWT fastai torch torchvision opencv-python pillow reportlab numpy python-dotenv

# Create requirements.txt
pip freeze > requirements.txt

cd ..

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Model files (too large for Git)
models/*.pkl
models/*.pth
models/*.h5

# Uploads and reports
uploads/*
!uploads/.gitkeep
reports/*
!reports/.gitkeep

# Database
*.db
*.sqlite
*.sqlite3

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
*.log

# Environment variables
.env
.env.local

# Testing
.pytest_cache/
.coverage
htmlcov/
EOF

# Create placeholder files
touch uploads/.gitkeep
touch reports/.gitkeep

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Train your model in Google Colab and download pneumonia_model.pkl"
echo "2. Place the model file in models/pneumonia_model.pkl"
echo "3. Copy all backend Python files to backend/"
echo "4. Copy all frontend files to frontend/"
echo "5. Update API_URL in all JS files"
echo "6. Run the backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "7. Run the frontend: cd frontend && python -m http.server 3000"
echo ""
```

### For Windows (setup.bat)

```batch
@echo off
REM Medical CDSS Quick Setup Script for Windows
REM Save this as: setup.bat
REM Run: setup.bat

echo Medical CDSS - Quick Setup
echo ==========================
echo.

REM Create project structure
echo Creating project directories...
mkdir backend frontend\css frontend\js models uploads reports 2>nul

REM Create __init__.py
type nul > backend\__init__.py

REM Backend setup
echo Setting up Python backend...
cd backend

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install --upgrade pip
pip install fastapi uvicorn python-multipart sqlalchemy pydantic python-jose passlib bcrypt PyJWT fastai torch torchvision opencv-python pillow reportlab numpy python-dotenv

REM Create requirements.txt
pip freeze > requirements.txt

cd ..

REM Create .gitignore
echo Creating .gitignore...
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo venv/
echo.
echo # Model files
echo models/*.pkl
echo.
echo # Uploads and reports
echo uploads/*
echo reports/*
echo.
echo # Database
echo *.db
echo.
echo # Environment
echo .env
) > .gitignore

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Train your model and place in models/pneumonia_model.pkl
echo 2. Copy all backend files to backend/
echo 3. Copy all frontend files to frontend/
echo 4. Update API_URL in JS files
echo 5. Run backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn main:app --reload
echo 6. Run frontend: cd frontend ^&^& python -m http.server 3000
echo.

pause
```

---

## 📝 Requirements.txt (Complete)

Create `backend/requirements.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
sqlalchemy==2.0.23
pydantic[email]==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.1
PyJWT==2.8.0
fastai==2.7.13
torch==2.1.0
torchvision==0.16.0
opencv-python==4.8.1.78
pillow==10.1.0
reportlab==4.0.7
numpy==1.24.3
python-dotenv==1.0.0
```

---

## 🔧 Environment Variables (.env)

Create `backend/.env`:

```env
# Security
SECRET_KEY=change-this-to-a-secure-random-string-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database
DATABASE_URL=sqlite:///./medical_cdss.db

# Model
MODEL_PATH=../models/pneumonia_model.pkl

# CORS (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# File Upload
MAX_UPLOAD_SIZE_MB=10

# API Configuration
API_TITLE=Medical CDSS API
API_VERSION=1.0.0
DEBUG_MODE=True
```

Then update `main.py` to use environment variables:

```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app = FastAPI(
    title=os.getenv("API_TITLE", "Medical CDSS API"),
    version=os.getenv("API_VERSION", "1.0.0"),
    debug=os.getenv("DEBUG_MODE", "False").lower() == "true"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📄 README.md Template

Create `README.md`:

````markdown
# Medical Clinical Decision Support System (CDSS)

AI-powered chest X-ray analysis system for detecting pneumonia, COVID-19, and tuberculosis.

## 🎯 Features

- Multi-disease detection (5 classes)
- Severity assessment (Mild, Moderate, Severe)
- Grad-CAM explainability
- Professional PDF report generation
- Doctor authentication system
- Patient records management
- Dark mode support
- Mobile responsive design

## 🛠️ Tech Stack

**Backend:**

- FastAPI
- FastAI (PyTorch)
- SQLAlchemy
- JWT Authentication
- ReportLab

**Frontend:**

- Vanilla JavaScript
- HTML5/CSS3
- Mobile-first design

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Trained FastAI model (`.pkl` file)

### Installation

1. Clone repository:

```bash
git clone <your-repo-url>
cd medical-cdss
```
````

2. Run setup script:

```bash
# Linux/Mac
chmod +x setup.sh
./setup.sh

# Windows
setup.bat
```

3. Place trained model:

```bash
cp /path/to/your/pneumonia_model.pkl models/
```

4. Start backend:

```bash
cd backend
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. Start frontend (new terminal):

```bash
cd frontend
python -m http.server 3000
```

6. Access application:

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 📊 Model Training

See Google Colab notebook for model training instructions.

## 🔒 Security

- JWT authentication
- Password hashing (bcrypt)
- CORS protection
- Rate limiting
- Input validation

## 📝 License

Educational purposes only. Not for clinical use without proper validation and certification.

## ⚠️ Disclaimer

This system is for educational purposes and must not be used for actual medical diagnosis without:

- FDA approval
- Clinical validation
- Healthcare professional oversight
- Appropriate medical device certification

````

---

## 🎨 API Configuration in JS Files

**Update in ALL JavaScript files** (`auth.js`, `dashboard.js`, `analysis.js`, `records.js`):

```javascript
// For local development
const API_URL = 'http://localhost:8000';

// For production (after deployment)
// const API_URL = 'https://your-backend-domain.com';

// Or use environment-based detection
const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://your-production-backend.com';
````

---

## 🐳 Docker Setup (Optional)

Create `Dockerfile` in backend directory:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml` in root:

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./models:/app/models
      - ./uploads:/app/uploads
      - ./reports:/app/reports
    environment:
      - SECRET_KEY=your-secret-key
      - DATABASE_URL=sqlite:///./medical_cdss.db

  frontend:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
```

Run with:

```bash
docker-compose up -d
```

---

## ✅ Post-Setup Checklist

- [ ] All directories created
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Model file in place (`models/pneumonia_model.pkl`)
- [ ] All backend files copied
- [ ] All frontend files copied
- [ ] API_URL updated in JS files
- [ ] SECRET_KEY changed in `main.py` or `.env`
- [ ] Backend running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] Can access login page
- [ ] Can register new account
- [ ] Can login successfully
- [ ] Can upload image and analyze
- [ ] Can view results
- [ ] Can download PDF report
- [ ] Can view patient records
- [ ] Dark mode working
- [ ] Mobile responsive

---

## 🎓 For Your Project Submission

Include:

1. This complete file structure
2. All source code files
3. README.md with setup instructions
4. Screenshots of the application
5. Model training notebook (Colab)
6. Documentation of your methodology
7. Sample output (PDF report)
8. Testing results
9. Future enhancements section

---

## 🆘 Common Issues & Solutions

**Issue:** "Module not found"

```bash
pip install -r requirements.txt
```

**Issue:** "Model file not found"

```bash
# Check model path
ls -la models/
# Ensure file name matches exactly: pneumonia_model.pkl
```

**Issue:** "CORS error"

```python
# In main.py, update:
allow_origins=["http://localhost:3000"]
```

**Issue:** "Port already in use"

```bash
# Use different port
uvicorn main:app --port 8001
```

**Issue:** "Database locked"

```bash
rm medical_cdss.db
# Restart backend (it will recreate)
```

---

## 🎉 You're Ready!

Follow the setup steps above, and your Medical CDSS will be fully operational!

For deployment to production, refer to the main deployment guide.
