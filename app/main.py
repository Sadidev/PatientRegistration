from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from . import models
from .database import SessionLocal, engine, Base
import asyncio
from pathlib import Path
import secrets
from pydantic import ValidationError

app = FastAPI(title="Patient Registration API")

# Constants for file upload
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

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
    db_patient = models.PatientDB(
        name=patient.name,
        email=patient.email,
        phone=patient.phone
    )
    
    try:
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
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/", response_model=List[models.PatientResponse])
def get_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    patients = db.query(models.PatientDB).offset(skip).limit(limit).all()
    return patients