from app.domain.dtos.DeliveryRecordDto import UpdateDeliveryQuantityResponseDto
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

class IDeliveryReportRepository(ABC):

    @abstractmethod
    def getSettlementReport(self, startDate: date, endDate: date, period: str, IdPointSale: Optional[int] = None, IdDomiciliary: Optional[int] = None) -> List[dict]:
        pass

    @abstractmethod
    def updateDeliveryQuantityFromReport(self, IdDeliveryRecord: int, deliveryQuantity: int) -> UpdateDeliveryQuantityResponseDto:
        pass