from app.domain.dtos.AbsenceTypeDto import AbsenceTypeResponseDto
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

class DeliveryRecordCreateDto(BaseModel):
    deliveryDate: date
    IdPointSale: int
    IdDomiciliary: int
    deliveryQuantity: Optional[int] = None
    IdAbsenceType: Optional[int] = None

class DeliveryRecordUpdateDto(BaseModel):
    deliveryDate: Optional[date] = None
    IdPointSale: Optional[int] = None
    IdDomiciliary: Optional[int] = None
    deliveryQuantity: Optional[int] = None
    IdAbsenceType: Optional[int] = None

class DeliverySettlementResponseDto(BaseModel):
    IdDeliverySettlement: int
    IdDeliveryRecord: int
    IdParameter: int
    parameterNameSettlement: str
    parameterValueSettlement: Decimal
    deliveryQuantitySettlement: int
    totalValueSettlement: Decimal
    createdBySettlement: str
    createdAtSettlement: datetime
    updatedBySettlement: Optional[str] = None
    updatedAtSettlement: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DeliveryRecordResponseDto(BaseModel):
    IdDeliveryRecord: int
    deliveryDate: date
    IdPointSale: int
    IdDomiciliary: int
    deliveryQuantity: int
    IdAbsenceType: Optional[int] = None
    absenceType: Optional[AbsenceTypeResponseDto] = None
    createdByDeliveryRecord: str
    createdAtDeliveryRecord: datetime
    updatedByDeliveryRecord: Optional[str] = None
    updatedAtDeliveryRecord: Optional[datetime] = None
    settlement: Optional[DeliverySettlementResponseDto] = None

    model_config = ConfigDict(from_attributes=True)

class DeliveryRecordBulkItemCreateDto(BaseModel):
    IdDomiciliary: int
    deliveryQuantity: Optional[int] = None
    IdAbsenceType: Optional[int] = None

class DeliveryRecordBulkCreateDto(BaseModel):
    deliveryDate: date
    IdPointSale: int
    records: List[DeliveryRecordBulkItemCreateDto]