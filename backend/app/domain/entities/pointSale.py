from sqlalchemy import Column, Integer, String, Boolean
from app.infrastructure.db.connection import Base

class pointSale(Base):
    __tablename__ = "pointSale"

    IdPointSale = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codePointSale = Column(String(50), nullable=False, unique=True)
    namePointSale = Column(String(150), nullable=False)
    statusPointSale = Column(Boolean, nullable=False, default=True)