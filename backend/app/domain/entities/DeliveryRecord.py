from sqlalchemy import Column, Integer, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import relationship

class DeliveryRecord(Base):
    __tablename__ = "DeliveryRecord"

    IdDeliveryRecord = Column(Integer, primary_key=True, index=True, autoincrement=True)
    deliveryDate = Column(Date, nullable=False)
    IdPointSale = Column(Integer, ForeignKey("pointSale.IdPointSale"), nullable=False)
    IdDomiciliary = Column(Integer, ForeignKey("Domiciliary.IdDomiciliary"), nullable=False)
    deliveryQuantity = Column(Integer, nullable=True)
    isRestDay = Column(Boolean, nullable=False, default=False)
    createdByDeliveryRecord = Column(Integer, nullable=False)
    createdAtDeliveryRecord = Column(DateTime, nullable=False)
    updatedByDeliveryRecord = Column(Integer, nullable=True)
    updatedAtDeliveryRecord = Column(DateTime, nullable=True)

    pointSaleRelation = relationship("pointSale")
    domiciliaryRelation = relationship("Domiciliary")
    settlement = relationship("DeliverySettlement", back_populates="deliveryRecord", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("deliveryDate", "IdPointSale", "IdDomiciliary", name="uq_delivery_record_daily"),)