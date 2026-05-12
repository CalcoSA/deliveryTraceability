from sqlalchemy import Column, Integer, String, Boolean
from app.infrastructure.db.connection import Base

class AbsenceType(Base):
    __tablename__ = "AbsenceType"

    IdAbsenceType = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nameAbsenceType = Column(String(100), nullable=False, unique=True)
    statusAbsenceType = Column(Boolean, nullable=False, default=True)