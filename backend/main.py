"""
FastAPI Backend for Medical CDSS
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import shutil
import os
from pathlib import Path
import jwt
import bcrypt

from models import (
    DoctorCreate, DoctorLogin, PatientRecord, AnalysisRequest,
    AnalysisResponse, Token
)
from database import engine, Base, get_db, Doctor, Patient, Analysis
from ml_inference import ModelInference
from report_generator import generate_pdf_report

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(title="Medical CDSS API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-change-in-production"  # Change this!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Initialize ML Model
model_inference = ModelInference("models/pneumonia_model.pkl")

# Create necessary directories
Path("uploads").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)


# ============================================================================
# Authentication Functions
# ============================================================================

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        doctor_id: int = payload.get("sub")
        if doctor_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return doctor_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    return {"message": "Medical CDSS API is running", "version": "1.0.0"}


@app.post("/api/auth/register", response_model=Token)
async def register_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    """Register a new doctor"""
    # Check if email exists
    existing_doctor = db.query(Doctor).filter(Doctor.email == doctor.email).first()
    if existing_doctor:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = bcrypt.hashpw(doctor.password.encode(), bcrypt.gensalt())
    
    # Create doctor
    new_doctor = Doctor(
        name=doctor.name,
        email=doctor.email,
        password=hashed_password.decode(),
        specialty=doctor.specialty,
        license_number=doctor.license_number
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    
    # Create token
    access_token = create_access_token(data={"sub": new_doctor.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "doctor_name": new_doctor.name,
        "doctor_id": new_doctor.id
    }


@app.post("/api/auth/login", response_model=Token)
async def login_doctor(credentials: DoctorLogin, db: Session = Depends(get_db)):
    """Login doctor"""
    doctor = db.query(Doctor).filter(Doctor.email == credentials.email).first()
    
    if not doctor:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not bcrypt.checkpw(credentials.password.encode(), doctor.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    access_token = create_access_token(data={"sub": doctor.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "doctor_name": doctor.name,
        "doctor_id": doctor.id
    }


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_xray(
    image: UploadFile = File(...),
    patient_name: str = Form(...),
    patient_age: int = Form(...),
    patient_gender: str = Form(...),
    symptoms: str = Form(...),
    medical_history: str = Form(""),
    temperature: Optional[float] = Form(None),
    oxygen_saturation: Optional[int] = Form(None),
    heart_rate: Optional[int] = Form(None),
    respiratory_rate: Optional[int] = Form(None),
    doctor_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Analyze chest X-ray and generate diagnosis"""
    
    # Save uploaded image temporarily
    image_path = f"uploads/{datetime.now().timestamp()}_{image.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    try:
        # Run ML inference
        prediction = model_inference.predict(image_path)
        
        # Create or get patient
        patient = db.query(Patient).filter(Patient.name == patient_name).first()
        if not patient:
            patient = Patient(
                name=patient_name,
                age=patient_age,
                gender=patient_gender,
                medical_history=medical_history
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
        
        # Save analysis
        analysis = Analysis(
            patient_id=patient.id,
            doctor_id=doctor_id,
            disease=prediction['disease'],
            severity=prediction['severity'],
            confidence=prediction['confidence'],
            symptoms=symptoms,
            temperature=temperature,
            oxygen_saturation=oxygen_saturation,
            heart_rate=heart_rate,
            respiratory_rate=respiratory_rate,
            image_path=image_path,
            gradcam_path=prediction['gradcam_path'],
            recommendations=", ".join(prediction['recommendations'])
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Generate PDF report
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        report_path = generate_pdf_report(
            analysis=analysis,
            patient=patient,
            doctor=doctor,
            prediction=prediction
        )
        
        # Update analysis with report path
        analysis.report_path = report_path
        db.commit()
        
        return AnalysisResponse(
            analysis_id=analysis.id,
            disease=prediction['disease'],
            severity=prediction['severity'],
            confidence=prediction['confidence'],
            affected_regions=prediction['affected_regions'],
            recommendations=prediction['recommendations'],
            gradcam_image=prediction['gradcam_path'],
            report_path=report_path,
            timestamp=analysis.timestamp.isoformat()
        )
        
    except Exception as e:
        # Clean up uploaded file on error
        if os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/records")
async def get_patient_records(
    doctor_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get all patient records for logged-in doctor"""
    analyses = db.query(Analysis).filter(Analysis.doctor_id == doctor_id).order_by(Analysis.timestamp.desc()).all()
    
    records = []
    for analysis in analyses:
        patient = db.query(Patient).filter(Patient.id == analysis.patient_id).first()
        records.append({
            "id": analysis.id,
            "patient_name": patient.name,
            "patient_age": patient.age,
            "patient_gender": patient.gender,
            "disease": analysis.disease,
            "severity": analysis.severity,
            "confidence": analysis.confidence,
            "timestamp": analysis.timestamp.isoformat(),
            "report_available": analysis.report_path is not None
        })
    
    return {"records": records}


@app.get("/api/records/{analysis_id}")
async def get_analysis_detail(
    analysis_id: int,
    doctor_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get detailed analysis information"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.doctor_id == doctor_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    patient = db.query(Patient).filter(Patient.id == analysis.patient_id).first()
    
    return {
        "patient": {
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "medical_history": patient.medical_history
        },
        "analysis": {
            "disease": analysis.disease,
            "severity": analysis.severity,
            "confidence": analysis.confidence,
            "symptoms": analysis.symptoms,
            "vital_signs": {
                "temperature": analysis.temperature,
                "oxygen_saturation": analysis.oxygen_saturation,
                "heart_rate": analysis.heart_rate,
                "respiratory_rate": analysis.respiratory_rate
            },
            "recommendations": analysis.recommendations,
            "timestamp": analysis.timestamp.isoformat(),
            "gradcam_available": analysis.gradcam_path is not None
        }
    }


@app.get("/api/download/report/{analysis_id}")
async def download_report(
    analysis_id: int,
    doctor_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Download PDF report"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.doctor_id == doctor_id
    ).first()
    
    if not analysis or not analysis.report_path:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not os.path.exists(analysis.report_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    patient = db.query(Patient).filter(Patient.id == analysis.patient_id).first()
    filename = f"report_{patient.name}_{analysis.timestamp.strftime('%Y%m%d')}.pdf"
    
    return FileResponse(
        analysis.report_path,
        media_type="application/pdf",
        filename=filename
    )


@app.get("/api/image/{image_type}/{analysis_id}")
async def get_image(
    image_type: str,
    analysis_id: int,
    doctor_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get original or Grad-CAM image"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.doctor_id == doctor_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    image_path = analysis.image_path if image_type == "original" else analysis.gradcam_path
    
    if not image_path or not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path)


@app.get("/api/stats")
async def get_statistics(
    doctor_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get statistics for dashboard"""
    total_analyses = db.query(Analysis).filter(Analysis.doctor_id == doctor_id).count()
    
    # Disease distribution
    diseases = db.query(Analysis.disease).filter(Analysis.doctor_id == doctor_id).all()
    disease_count = {}
    for (disease,) in diseases:
        disease_count[disease] = disease_count.get(disease, 0) + 1
    
    # Recent analyses
    recent = db.query(Analysis).filter(Analysis.doctor_id == doctor_id).order_by(Analysis.timestamp.desc()).limit(5).all()
    
    return {
        "total_analyses": total_analyses,
        "disease_distribution": disease_count,
        "recent_count": len(recent)
    }