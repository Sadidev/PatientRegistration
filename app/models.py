from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

class PatientDB(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    address = Column(String(100))
    phone = Column(String(20))
    document_path = Column(String(255), nullable=True)

class PatientCreate(BaseModel):
    name: constr(min_length=2, max_length=100)
    email: EmailStr
    phone: constr(pattern=r'^\+?1?\d{9,15}$')
    address: constr(max_length=100)

class PatientResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    address: str
    document_path: Optional[str]

    class Config:
        orm_mode = True