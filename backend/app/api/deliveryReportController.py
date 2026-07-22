from app.domain.dtos.DeliveryRecordDto import ( UpdateDeliveryQuantityRequestDto, UpdateDeliveryQuantityResponseDto )
from app.infrastructure.repositories.DeliveryReportRepository import DeliveryReportRepository
from app.application.interfaces.IDeliveryReportApplication import IDeliveryReportApplication
from app.application.services.DeliveryReportApplication import DeliveryReportApplication
from app.domain.dtos.DeliveryReportDto import ( DeliverySettlementReportResponseDto )
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.api.authController import getCurrentPayload
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/delivery-report", tags=["delivery-report"])
logger = getLogger(__name__)

def getDeliveryReportApplication(db: Session = Depends(getDb)) -> IDeliveryReportApplication:
    deliveryReportRepository = DeliveryReportRepository(db)
    return DeliveryReportApplication(deliveryReportRepository)

@router.get("/settlement", response_model=apiResponseDto[List[DeliverySettlementReportResponseDto]])
def getSettlementReport(startDate: date = Query(...), endDate: date = Query(...), period: str = Query("day"), IdPointSale: Optional[int] = Query(None), IdDomiciliary: Optional[int] = Query(None), payload: dict = Depends(getCurrentPayload), service: IDeliveryReportApplication = Depends(getDeliveryReportApplication)):
    try:
        logger.info("Consultando reporte de domicilios | startDate=%s | endDate=%s | period=%s | IdPointSale=%s | IdDomiciliary=%s", startDate, endDate, period, IdPointSale, IdDomiciliary)
        data = service.getSettlementReport(startDate=startDate, endDate=endDate, period=period, IdPointSale=IdPointSale, IdDomiciliary=IdDomiciliary)

        if not data:
            logger.info("Reporte de domicilios sin datos | startDate=%s | endDate=%s | period=%s | IdPointSale=%s | IdDomiciliary=%s", startDate, endDate, period, IdPointSale, IdDomiciliary)
            return apiResponseDto(isSuccess=False, Message="No existen datos para el reporte con los filtros enviados.", result=[])
        
        logger.info("Reporte de domicilios obtenido correctamente | total=%s | startDate=%s | endDate=%s", len(data), startDate, endDate)
        return apiResponseDto(isSuccess=True, Message="Reporte obtenido correctamente.", result=data)

    except ValueError as e:
        logger.warning("Validación fallida obteniendo reporte de domicilios | startDate=%s | endDate=%s | period=%s | IdPointSale=%s | IdDomiciliary=%s | error=%s", startDate, endDate, period, IdPointSale, IdDomiciliary, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo reporte de domicilios | startDate=%s | endDate=%s | period=%s | IdPointSale=%s | IdDomiciliary=%s", startDate, endDate, period, IdPointSale, IdDomiciliary)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el reporte de domicilios.")
    
@router.put("/settlement/{IdDeliveryRecord}/quantity", response_model=apiResponseDto[UpdateDeliveryQuantityResponseDto])
def updateDeliveryQuantityFromReport(IdDeliveryRecord: int, request: UpdateDeliveryQuantityRequestDto, payload: dict = Depends(getCurrentPayload), service: IDeliveryReportApplication = Depends(getDeliveryReportApplication)):
    try:
        logger.info("Actualizando cantidad de domicilios desde reporte | IdDeliveryRecord=%s | deliveryQuantity=%s", IdDeliveryRecord, request.deliveryQuantity, request.IdAbsenceType)
        data = service.updateDeliveryQuantityFromReport(IdDeliveryRecord=IdDeliveryRecord, deliveryQuantity=request.deliveryQuantity, IdAbsenceType=request.IdAbsenceType)
        logger.info("Cantidad de domicilios actualizada correctamente desde reporte | IdDeliveryRecord=%s | totalValueSettlement=%s", IdDeliveryRecord, data.totalValueSettlement)
        return apiResponseDto(isSuccess=True, Message="Cantidad de domicilios actualizada correctamente.", result=data)

    except ValueError as e:
        logger.warning("Validación fallida actualizando cantidad desde reporte | IdDeliveryRecord=%s | error=%s", IdDeliveryRecord, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado actualizando cantidad desde reporte | IdDeliveryRecord=%s", IdDeliveryRecord)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar la cantidad de domicilios.")