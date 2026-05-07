from app.domain.dtos.DeliveryReportDto import DeliverySettlementReportResponseDto
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

class IDeliveryReportApplication(ABC):

    @abstractmethod
    def getSettlementReport(self, startDate: date, endDate: date, period: str, IdPointSale: Optional[int] = None, IdDomiciliary: Optional[int] = None) -> List[DeliverySettlementReportResponseDto]:
        pass