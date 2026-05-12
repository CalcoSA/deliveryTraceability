from sqlalchemy import Column, Integer, String, DateTime
from app.infrastructure.db.connection import Base

class ParameterHistory(Base):
    __tablename__ = "ParameterHistory"

    IdParameterHistory = Column(Integer, primary_key=True, index=True, autoincrement=True)
    IdParameter = Column(Integer, nullable=False, index=True)
    actionParameterHistory = Column(String(20), nullable=False)
    previousNameParameter = Column(String(100), nullable=True)
    newNameParameter = Column(String(100), nullable=True)
    previousValueParameter = Column(String(500), nullable=True)
    newValueParameter = Column(String(500), nullable=True)
    createdByParameterHistory = Column(String(100), nullable=False)
    createdAtParameterHistory = Column(DateTime, nullable=False)