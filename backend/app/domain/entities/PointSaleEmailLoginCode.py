from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import relationship

class PointSaleEmailLoginCode(Base):
    __tablename__ = "PointSaleEmailLoginCode"

    IdPointSaleEmailLoginCode = Column(Integer, primary_key=True, index=True, autoincrement=True)
    IdPointSaleEmail = Column(Integer, ForeignKey("PointSaleEmail.IdPointSaleEmail"), nullable=False)
    codeHash = Column(String(150), nullable=False)
    attempts = Column(Integer, nullable=False, default=0)
    expiresAt = Column(DateTime, nullable=False)
    usedAt = Column(DateTime, nullable=True)
    createdAt = Column(DateTime, nullable=False)

    pointSaleEmailRelation = relationship("PointSaleEmail")