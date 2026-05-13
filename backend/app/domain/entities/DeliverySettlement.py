from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import relationship

class DeliverySettlement(Base):
    __tablename__ = "DeliverySettlement"

    IdDeliverySettlement = Column(Integer, primary_key=True, index=True, autoincrement=True)
    IdDeliveryRecord = Column(Integer, ForeignKey("DeliveryRecord.IdDeliveryRecord"), nullable=False)
    IdParameter = Column(Integer, ForeignKey("Parameter.IdParameter"), nullable=False)
    parameterNameSettlement = Column(String(100), nullable=False)
    parameterValueSettlement = Column(Numeric(12, 2), nullable=False)
    deliveryQuantitySettlement = Column(Integer, nullable=False)
    totalValueSettlement = Column(Numeric(14, 2), nullable=False)
    createdBySettlement = Column(String(150), nullable=False)
    createdAtSettlement = Column(DateTime, nullable=False)
    updatedBySettlement = Column(String(150), nullable=True)
    updatedAtSettlement = Column(DateTime, nullable=True)
    
    deliveryRecord = relationship("DeliveryRecord", back_populates="settlement")
    parameterRelation = relationship("Parameter")

    __table_args__ = (UniqueConstraint("IdDeliveryRecord", name="uq_delivery_settlement_record"),)