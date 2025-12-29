"""
Backend auth.py - Authentication and Authorization Utilities
Save this as: backend/auth.py
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import bcrypt

from database import get_db, Doctor

# Security Configuration
SECRET_KEY = "your-secret-key-change-in-production"  # CHANGE THIS IN PRODUCTION!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer for token authentication
security = HTTPBearer()


# ============================================================================
# Password Hashing Functions
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT Token Functions
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing claims to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary containing decoded claims
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# Authentication Dependencies
# ============================================================================

def get_current_doctor_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Get the current authenticated doctor's ID from JWT token
    
    Args:
        credentials: HTTP Bearer credentials containing JWT token
        
    Returns:
        Doctor ID (integer)
        
    Raises:
        HTTPException: If token is invalid, expired, or missing doctor ID
    """
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        doctor_id: int = payload.get("sub")
        
        if doctor_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return doctor_id
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_doctor(
    doctor_id: int = Depends(get_current_doctor_id),
    db: Session = Depends(get_db)
) -> Doctor:
    """
    Get the current authenticated doctor object from database
    
    Args:
        doctor_id: Doctor ID from JWT token
        db: Database session
        
    Returns:
        Doctor object from database
        
    Raises:
        HTTPException: If doctor not found in database
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    return doctor


# ============================================================================
# Authentication Helper Functions
# ============================================================================

def authenticate_doctor(email: str, password: str, db: Session) -> Optional[Doctor]:
    """
    Authenticate a doctor by email and password
    
    Args:
        email: Doctor's email address
        password: Plain text password
        db: Database session
        
    Returns:
        Doctor object if authentication successful, None otherwise
    """
    doctor = db.query(Doctor).filter(Doctor.email == email).first()
    
    if not doctor:
        return None
    
    if not verify_password(password, doctor.password):
        return None
    
    return doctor


def create_doctor_token(doctor: Doctor) -> dict:
    """
    Create access token and return token data for a doctor
    
    Args:
        doctor: Doctor object from database
        
    Returns:
        Dictionary containing access token and user info
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": doctor.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "doctor_id": doctor.id,
        "doctor_name": doctor.name,
        "doctor_email": doctor.email,
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    }


# ============================================================================
# Authorization Helper Functions
# ============================================================================

def check_doctor_owns_analysis(doctor_id: int, analysis_doctor_id: int) -> bool:
    """
    Check if a doctor owns a specific analysis
    
    Args:
        doctor_id: ID of current doctor
        analysis_doctor_id: ID of doctor who created the analysis
        
    Returns:
        True if doctor owns the analysis, False otherwise
    """
    return doctor_id == analysis_doctor_id


def require_doctor_owns_analysis(doctor_id: int, analysis_doctor_id: int):
    """
    Require that a doctor owns a specific analysis, raise exception if not
    
    Args:
        doctor_id: ID of current doctor
        analysis_doctor_id: ID of doctor who created the analysis
        
    Raises:
        HTTPException: If doctor doesn't own the analysis
    """
    if not check_doctor_owns_analysis(doctor_id, analysis_doctor_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )


# ============================================================================
# Token Validation Functions
# ============================================================================

def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token is expired
    
    Args:
        token: JWT token string
        
    Returns:
        True if token is expired, False otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if exp is None:
            return True
        return datetime.utcnow() > datetime.fromtimestamp(exp)
    except JWTError:
        return True


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get the expiration datetime of a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Datetime object of token expiration, or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if exp is None:
            return None
        return datetime.fromtimestamp(exp)
    except JWTError:
        return None


# ============================================================================
# Rate Limiting Helper (Optional - for production)
# ============================================================================

class RateLimiter:
    """
    Simple in-memory rate limiter for authentication attempts
    Use Redis in production for distributed systems
    """
    
    def __init__(self):
        self.attempts = {}  # email -> list of attempt timestamps
        self.max_attempts = 5
        self.window_seconds = 300  # 5 minutes
    
    def is_rate_limited(self, email: str) -> bool:
        """Check if email is rate limited"""
        now = datetime.utcnow()
        
        if email not in self.attempts:
            return False
        
        # Remove old attempts outside the window
        self.attempts[email] = [
            timestamp for timestamp in self.attempts[email]
            if (now - timestamp).total_seconds() < self.window_seconds
        ]
        
        # Check if too many attempts
        return len(self.attempts[email]) >= self.max_attempts
    
    def record_attempt(self, email: str):
        """Record a failed authentication attempt"""
        now = datetime.utcnow()
        
        if email not in self.attempts:
            self.attempts[email] = []
        
        self.attempts[email].append(now)
    
    def clear_attempts(self, email: str):
        """Clear attempts for an email (after successful login)"""
        if email in self.attempts:
            del self.attempts[email]


# Create global rate limiter instance
rate_limiter = RateLimiter()


# ============================================================================
# Example Usage in FastAPI Routes
# ============================================================================

"""
# In your main.py or routes file:

from auth import (
    get_current_doctor, 
    authenticate_doctor, 
    create_doctor_token,
    hash_password,
    rate_limiter
)

@app.post("/api/auth/login")
async def login(credentials: LoginSchema, db: Session = Depends(get_db)):
    # Check rate limiting
    if rate_limiter.is_rate_limited(credentials.email):
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again later."
        )
    
    # Authenticate doctor
    doctor = authenticate_doctor(credentials.email, credentials.password, db)
    
    if not doctor:
        rate_limiter.record_attempt(credentials.email)
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Clear rate limiting on successful login
    rate_limiter.clear_attempts(credentials.email)
    
    # Create and return token
    return create_doctor_token(doctor)


@app.post("/api/auth/register")
async def register(data: RegisterSchema, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = db.query(Doctor).filter(Doctor.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new doctor
    new_doctor = Doctor(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        specialty=data.specialty,
        license_number=data.license_number
    )
    
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    
    # Return token
    return create_doctor_token(new_doctor)


@app.get("/api/protected-route")
async def protected_route(
    current_doctor: Doctor = Depends(get_current_doctor)
):
    return {
        "message": "This is a protected route",
        "doctor": current_doctor.name
    }
"""


# ============================================================================
# Security Best Practices Notes
# ============================================================================

"""
PRODUCTION SECURITY CHECKLIST:

1. Change SECRET_KEY to a secure random string:
   import secrets
   SECRET_KEY = secrets.token_urlsafe(32)

2. Store SECRET_KEY in environment variable:
   SECRET_KEY = os.getenv("SECRET_KEY")

3. Use HTTPS in production (SSL/TLS)

4. Implement proper rate limiting (use Redis in production)

5. Add refresh tokens for long-lived sessions

6. Implement password complexity requirements

7. Add account lockout after failed attempts

8. Log authentication events for security auditing

9. Implement 2FA/MFA for additional security

10. Use secure session storage

11. Implement CSRF protection

12. Add input validation and sanitization

13. Use prepared statements to prevent SQL injection

14. Implement proper error handling (don't leak info)

15. Regular security audits and updates

16. Comply with relevant regulations (HIPAA, GDPR)
"""