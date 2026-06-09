from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint, String
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import relationship

class DeliveryRecord(Base):
    __tablename__ = "DeliveryRecord"

    IdDeliveryRecord = Column(Integer, primary_key=True, index=True, autoincrement=True)
    deliveryDate = Column(Date, nullable=False)
    IdPointSale = Column(Integer, ForeignKey("pointSale.IdPointSale"), nullable=False)
    IdDomiciliary = Column(Integer, ForeignKey("Domiciliary.IdDomiciliary"), nullable=False)
    deliveryQuantity = Column(Integer, nullable=False, default=0)
    IdAbsenceType = Column(Integer, ForeignKey("AbsenceType.IdAbsenceType"), nullable=True)
    createdByDeliveryRecord = Column(String(150), nullable=False)
    createdAtDeliveryRecord = Column(DateTime, nullable=False)
    updatedByDeliveryRecord = Column(String(150), nullable=True)
    updatedAtDeliveryRecord = Column(DateTime, nullable=True)

    pointSaleRelation = relationship("pointSale")
    domiciliaryRelation = relationship("Domiciliary")
    absenceTypeRelation = relationship("AbsenceType")
    settlement = relationship("DeliverySettlement", back_populates="deliveryRecord", uselist=False, cascade="all, delete-orphan")

    @property
    def absenceType(self):
        return self.absenceTypeRelation

    __table_args__ = (UniqueConstraint("deliveryDate", "IdPointSale", "IdDomiciliary", name="uq_delivery_record_daily"),)