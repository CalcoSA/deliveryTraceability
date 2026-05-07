from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class DeliverySettlementReportResponseDto(BaseModel):
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
    totalRestDays: int
    totalValueSettlement: Decimal
    totalRecords: int
    createdByUsers: Optional[str] = None