from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import relationship

class Domiciliary(Base):
    __tablename__ = "Domiciliary"

    IdDomiciliary = Column(Integer, primary_key=True, index=True, autoincrement=True)
    documentDomiciliary = Column(String(20), nullable=False, unique=True)
    nameDomiciliary = Column(String(150), nullable=False)
    statusDomiciliary = Column(Boolean, nullable=False, default=True)
    pointSale = Column(Integer, ForeignKey("pointSale.IdPointSale"), nullable=False)

    pointSaleRelation = relationship("pointSale")