from sqlalchemy import Column, Integer, String, DateTime
from app.infrastructure.db.connection import Base

class Parameter(Base):
    __tablename__ = "Parameter"

    IdParameter = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nameParameter = Column(String(100), nullable=False, unique=True)
    valueParameter = Column(String(500), nullable=False)
    createdByParameter = Column(String(100), nullable=False)
    createdAtParameter = Column(DateTime, nullable=False)
    updatedByParameter = Column(String(100), nullable=True)
    updatedAtParameter = Column(DateTime, nullable=True)