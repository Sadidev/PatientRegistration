from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from .database import Base, engine
from .config import settings

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
    name: str = Field(
        min_length=2, 
        max_length=100,
        pattern="^[a-zA-Z ]+$",
        description="Patient's full name (letters and spaces only)"
    )
    email: EmailStr
    phone: str = Field(
        pattern=r"^\+?1?\d{9,15}$",
        description="Phone number in international format"
    )
    address: str = Field(
        min_length=5,
        max_length=200,
        description="Physical address"
    )
class PatientResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    address: str
    document_path: Optional[str]

    class Config:
        orm_mode = True