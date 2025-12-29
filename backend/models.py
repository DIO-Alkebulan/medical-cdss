"""
Pydantic Models for Request/Response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class DoctorCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    specialty: str
    license_number: str


class DoctorLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    doctor_name: str
    doctor_id: int


class PatientRecord(BaseModel):
    name: str
    age: int
    gender: str
    medical_history: Optional[str] = ""


class AnalysisRequest(BaseModel):
    patient_name: str
    patient_age: int
    patient_gender: str
    symptoms: str
    medical_history: Optional[str] = ""
    temperature: Optional[float] = None
    oxygen_saturation: Optional[int] = None
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None


class AnalysisResponse(BaseModel):
    analysis_id: int
    disease: str
    severity: str
    confidence: float
    affected_regions: List[str]
    recommendations: List[str]
    gradcam_image: str
    report_path: str
    timestamp: str