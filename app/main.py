from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from typing import List, Annotated
import asyncio
import logging
from datetime import datetime

from .database import SessionLocal, engine, Base
from . import models
from .services import email_service, file_service, patient_service

# Initialize settings from config
settings = models.Settings()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Setup logging configuration
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
    }
})

logger = logging.getLogger(__name__)

# Create uploads directory
settings.UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize database
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Patient Registration API",
    description="API for managing patient registrations and documents",
    version="1.0.0"
)

# Exception Handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"Integrity error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=400,
        content={"detail": "Database integrity error occurred"},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {duration:.3f}s"
    )
    return response

# Routes
@app.post("/patients/", response_model=models.PatientResponse)
async def create_patient(
    patient: models.PatientCreate = Depends(),
    document: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        # Check for existing patient
        if await patient_service.patient_exists(db, patient.email):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Create patient record
        db_patient = models.PatientDB(**patient.model_dump())

        # Handle document upload
        if document:
            document_path = await file_service.save_file(
                document,
                settings.UPLOAD_DIR,
                settings.MAX_FILE_SIZE,
                settings.ALLOWED_EXTENSIONS
            )
            db_patient.document_path = document_path

        # Save to database
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)

        # Send confirmation email asynchronously
        asyncio.create_task(
            email_service.send_confirmation_email(patient.email)
        )

        return db_patient

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating patient: {e}", exc_info=True)
        raise JSONResponse(status_code=e.status_code, content={"detail": e.detail})

@app.get("/patients/", response_model=List[models.PatientResponse])
async def get_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return await patient_service.get_patients(db, skip, limit)

@app.get("/uploads/{filename}")
async def get_file(filename: str):
    file_path = settings.UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)