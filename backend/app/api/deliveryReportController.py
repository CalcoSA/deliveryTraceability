from app.infrastructure.repositories.DeliveryReportRepository import DeliveryReportRepository
from app.application.interfaces.IDeliveryReportApplication import IDeliveryReportApplication
from app.application.services.DeliveryReportApplication import DeliveryReportApplication
from app.domain.dtos.DeliveryReportDto import DeliverySettlementReportResponseDto
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.api.authController import getCurrentPayload
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/delivery-report", tags=["delivery-report"])

def getDeliveryReportApplication(db: Session = Depends(getDb)) -> IDeliveryReportApplication:
    deliveryReportRepository = DeliveryReportRepository(db)
    return DeliveryReportApplication(deliveryReportRepository)

@router.get("/settlement", response_model=apiResponseDto[List[DeliverySettlementReportResponseDto]])
def getSettlementReport(startDate: date = Query(...), endDate: date = Query(...), period: str = Query("day"), IdPointSale: Optional[int] = Query(None), IdDomiciliary: Optional[int] = Query(None), payload: dict = Depends(getCurrentPayload), service: IDeliveryReportApplication = Depends(getDeliveryReportApplication)):
    try:
        data = service.getSettlementReport(startDate=startDate, endDate=endDate, period=period, IdPointSale=IdPointSale, IdDomiciliary=IdDomiciliary)

        if not data:
            return apiResponseDto(isSuccess=False, Message="No existen datos para el reporte con los filtros enviados.", result=[])

        return apiResponseDto(isSuccess=True, Message="Reporte obtenido correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        print("ERROR REAL OBTENIENDO REPORTE DE DOMICILIOS:", repr(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el reporte de domicilios.")