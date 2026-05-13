from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.infrastructure.db.connection import Base

class PointSaleEmail(Base):
    __tablename__ = "PointSaleEmail"

    IdPointSaleEmail = Column(Integer, primary_key=True, index=True, autoincrement=True)
    emailPointSale = Column(String(150), nullable=False, unique=True)
    statusPointSaleEmail = Column(Boolean, nullable=False, default=True)
    createdAtPointSaleEmail = Column(DateTime, nullable=False)
    updatedAtPointSaleEmail = Column(DateTime, nullable=True)