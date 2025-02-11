from sqlalchemy.orm import Session
from typing import List
from ..models import PatientDB

async def patient_exists(db: Session, email: str) -> bool:
    return db.query(PatientDB).filter_by(email=email).first() is not None

async def get_patients(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[PatientDB]:
    return db.query(PatientDB).offset(skip).limit(limit).all()