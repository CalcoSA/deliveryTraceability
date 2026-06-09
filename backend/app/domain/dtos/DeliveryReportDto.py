from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional

class DeliverySettlementReportResponseDto(BaseModel):
    IdDeliveryRecord: Optional[int] = None
    periodType: str
    periodKey: str
    periodLabel: str
    IdPointSale: int
    codePointSale: str
    namePointSale: str
    IdDomiciliary: int
    documentDomiciliary: str
    nameDomiciliary: str
    parameterNameSettlement: str
    parameterValueSettlement: Decimal
    totalDeliveryQuantity: int
    totalAbsences: int
    absenceTypes: str = ""
    totalValueSettlement: Decimal
    totalRecords: int
    createdByUsers: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)