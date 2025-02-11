import asyncio
import secrets
import logging
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from typing import List
from pathlib import Path
from . import models
from .database import SessionLocal, engine, Base

# Constants for file upload
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Patient Registration API")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Handle Pydantic Validation Errors
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Handle SQLAlchemy Integrity Errors
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"Integrity error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Database integrity error. Maybe a duplicate entry?"},
    )

# Handle General Errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )

# Create uploads directory if it doesn't exist
UPLOAD_DIR.mkdir(exist_ok=True)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def send_confirmation_email(email: str):
    # This would be replaced with your actual email sending logic
    await asyncio.sleep(1)  # Simulate email sending
    print(f"Confirmation email sent to {email}")

async def save_upload_file(upload_file: UploadFile) -> str:
    # Validate file size
    contents = await upload_file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
        
    # Create secure random filename
    file_extension = Path(upload_file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")
        
    random_filename = f"{secrets.token_urlsafe(16)}{file_extension}"
    file_path = UPLOAD_DIR / random_filename
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not save file")
        
    return str(file_path)

@app.post("/patients/", response_model=models.PatientResponse)
async def create_patient(
    patient: models.PatientCreate = Depends(),
    document: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    
    try:
        # Check for duplicate emails
        existing_patient = db.query(models.PatientDB).filter_by(email=patient.email).first()
        logger.error(f"Email exists: {existing_patient}")

        if existing_patient:
            logger.error(f"Email exists")
            raise HTTPException(status_code=400, detail="Email already exists")

        db_patient = models.PatientDB(**patient.model_dump())

        if document:
            document_path = await save_upload_file(document)
            db_patient.document_path = document_path
        
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        
        # Asynchronously send confirmation email
        asyncio.create_task(send_confirmation_email(patient.email))
        
        return db_patient
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating patient: {e}")
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

@app.get("/patients/", response_model=List[models.PatientResponse])
def get_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    patients = db.query(models.PatientDB).offset(skip).limit(limit).all()
    return patients