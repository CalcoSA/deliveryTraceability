from app.application.interfaces.IDeliveryReportApplication import IDeliveryReportApplication
from app.domain.interfaces.IDeliveryReportRepository import IDeliveryReportRepository
from app.domain.dtos.DeliveryReportDto import DeliverySettlementReportResponseDto
from typing import List, Optional
from datetime import date

class DeliveryReportApplication(IDeliveryReportApplication):

    VALID_PERIODS = ["day", "week", "month"]

    def __init__(self, deliveryReportRepository: IDeliveryReportRepository):
        self.deliveryReportRepository = deliveryReportRepository

    def getSettlementReport(self, startDate: date, endDate: date, period: str, IdPointSale: Optional[int] = None, IdDomiciliary: Optional[int] = None) -> List[DeliverySettlementReportResponseDto]:
        cleanPeriod = period.strip().lower()

        if cleanPeriod not in self.VALID_PERIODS:
            raise ValueError("El periodo debe ser day, week o month.")

        if endDate < startDate:
            raise ValueError("La fecha final no puede ser menor que la fecha inicial.")

        return self.deliveryReportRepository.getSettlementReport(startDate=startDate, endDate=endDate, period=cleanPeriod, IdPointSale=IdPointSale, IdDomiciliary=IdDomiciliary)