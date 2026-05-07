from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from typing import List

class DeliveryRecordCreateDto(BaseModel):
    deliveryDate: date
    IdPointSale: int
    IdDomiciliary: int
    deliveryQuantity: Optional[int] = None
    isRestDay: bool = False

class DeliveryRecordUpdateDto(BaseModel):
    deliveryDate: Optional[date] = None
    IdPointSale: Optional[int] = None
    IdDomiciliary: Optional[int] = None
    deliveryQuantity: Optional[int] = None
    isRestDay: Optional[bool] = None

class DeliverySettlementResponseDto(BaseModel):
    IdDeliverySettlement: int
    IdDeliveryRecord: int
    IdParameter: int
    parameterNameSettlement: str
    parameterValueSettlement: Decimal
    deliveryQuantitySettlement: int
    totalValueSettlement: Decimal
    createdBySettlement: int
    createdAtSettlement: datetime
    updatedBySettlement: Optional[int] = None
    updatedAtSettlement: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DeliveryRecordResponseDto(BaseModel):
    IdDeliveryRecord: int
    deliveryDate: date
    IdPointSale: int
    IdDomiciliary: int
    deliveryQuantity: Optional[int] = None
    isRestDay: bool
    createdByDeliveryRecord: int
    createdAtDeliveryRecord: datetime
    updatedByDeliveryRecord: Optional[int] = None
    updatedAtDeliveryRecord: Optional[datetime] = None
    settlement: Optional[DeliverySettlementResponseDto] = None

    model_config = ConfigDict(from_attributes=True)

class DeliveryRecordBulkItemCreateDto(BaseModel):
    IdDomiciliary: int
    deliveryQuantity: Optional[int] = None
    isRestDay: bool = False

class DeliveryRecordBulkCreateDto(BaseModel):
    deliveryDate: date
    IdPointSale: int
    records: List[DeliveryRecordBulkItemCreateDto]