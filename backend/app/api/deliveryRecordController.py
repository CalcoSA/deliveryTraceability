from app.domain.dtos.DeliveryRecordDto import (DeliveryRecordCreateDto, DeliveryRecordUpdateDto, DeliveryRecordResponseDto, DeliveryRecordBulkCreateDto)
from app.infrastructure.repositories.DeliveryRecordRepository import DeliveryRecordRepository
from app.application.interfaces.IDeliveryRecordApplication import IDeliveryRecordApplication
from app.application.services.DeliveryRecordApplication import DeliveryRecordApplication
from app.infrastructure.repositories.DomiciliaryRepository import DomiciliaryRepository
from app.infrastructure.repositories.AbsenceTypeRepository import AbsenceTypeRepository
from app.infrastructure.repositories.pointSaleRepository import pointSaleRepository
from app.infrastructure.repositories.ParameterRepository import ParameterRepository
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.api.authController import getCurrentPayload
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/delivery-record", tags=["delivery-record"])
logger = getLogger(__name__)

def getDeliveryRecordApplication(db: Session = Depends(getDb)) -> IDeliveryRecordApplication:
    deliveryRecordRepository = DeliveryRecordRepository(db)
    pointSaleRepo = pointSaleRepository(db)
    domiciliaryRepo = DomiciliaryRepository(db)
    parameterRepo = ParameterRepository(db)
    absenceTypeRepo = AbsenceTypeRepository(db)

    return DeliveryRecordApplication(deliveryRecordRepository, pointSaleRepo, domiciliaryRepo, parameterRepo, absenceTypeRepo)

def getAuthenticatedUserId(payload: dict) -> int:
    userId = payload.get("wordpressUserId")

    if not userId:
        logger.warning("No se pudo identificar el usuario autenticado en el payload.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo identificar el usuario autenticado.")

    return int(userId)

@router.get("/", response_model=apiResponseDto[List[DeliveryRecordResponseDto]])
def getAllDeliveryRecords(deliveryDate: Optional[date] = Query(None), IdPointSale: Optional[int] = Query(None), IdDomiciliary: Optional[int] = Query(None), payload: dict = Depends(getCurrentPayload), service: IDeliveryRecordApplication = Depends(getDeliveryRecordApplication)):
    try:
        logger.info("Consultando registros de domicilios | deliveryDate=%s | IdPointSale=%s | IdDomiciliary=%s", deliveryDate, IdPointSale, IdDomiciliary)
        data = service.getAll(deliveryDate, IdPointSale, IdDomiciliary)

        if not data:
            logger.info("No existen registros de domicilios para los filtros enviados.")
            return apiResponseDto(isSuccess=False, Message="No existen registros de domicilios.", result=[])

        logger.info("Registros de domicilios obtenidos correctamente | total=%s", len(data))
        return apiResponseDto(isSuccess=True, Message="Registros de domicilios obtenidos correctamente.", result=data)

    except Exception:
        logger.exception("Error inesperado obteniendo registros de domicilios | deliveryDate=%s | IdPointSale=%s | IdDomiciliary=%s", deliveryDate, IdPointSale, IdDomiciliary)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros de domicilios.")

@router.get("/{IdDeliveryRecord}", response_model=apiResponseDto[DeliveryRecordResponseDto])
def getDeliveryRecordById(IdDeliveryRecord: int, payload: dict = Depends(getCurrentPayload), service: IDeliveryRecordApplication = Depends(getDeliveryRecordApplication)):
    try:
        logger.info("Consultando registro de domicilio | IdDeliveryRecord=%s", IdDeliveryRecord)
        data = service.getById(IdDeliveryRecord)
        logger.info("Registro de domicilio obtenido correctamente | IdDeliveryRecord=%s", IdDeliveryRecord)
        return apiResponseDto(isSuccess=True, Message="Registro de domicilio obtenido correctamente.", result=data)

    except ValueError as e:
        logger.warning("Registro de domicilio no encontrado | IdDeliveryRecord=%s | error=%s", IdDeliveryRecord, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.exception("Error inesperado obteniendo registro de domicilio | IdDeliveryRecord=%s", IdDeliveryRecord)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro de domicilio.")

@router.post("/", response_model=apiResponseDto[DeliveryRecordResponseDto], status_code=status.HTTP_201_CREATED)
def createDeliveryRecord(deliveryData: DeliveryRecordCreateDto, payload: dict = Depends(getCurrentPayload), service: IDeliveryRecordApplication = Depends(getDeliveryRecordApplication)):
    try:
        userId = getAuthenticatedUserId(payload)
        logger.info("Creando registro de domicilio | userId=%s", userId)
        data = service.create(deliveryData, userId)
        logger.info("Registro de domicilio creado correctamente | IdDeliveryRecord=%s | userId=%s", getattr(data, "IdDeliveryRecord", None), userId)
        return apiResponseDto(isSuccess=True, Message="Registro de domicilio creado correctamente.", result=data)

    except ValueError as e:
        logger.warning("Validación creando registro de domicilio | error=%s", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except HTTPException:
        raise

    except Exception:
        logger.exception("Error inesperado creando registro de domicilio.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro de domicilio.")
    
@router.post("/bulk", response_model=apiResponseDto[List[DeliveryRecordResponseDto]], status_code=status.HTTP_201_CREATED)
def createManyDeliveryRecords(deliveryData: DeliveryRecordBulkCreateDto, payload: dict = Depends(getCurrentPayload), service: IDeliveryRecordApplication = Depends(getDeliveryRecordApplication)):
    try:
        userId = getAuthenticatedUserId(payload)
        logger.info("Creando registros masivos de domicilio | userId=%s", userId)
        data = service.createMany(deliveryData, userId)
        logger.info("Registros masivos de domicilio creados correctamente | total=%s | userId=%s", len(data), userId)
        return apiResponseDto(isSuccess=True, Message="Registros de domicilios creados correctamente.", result=data)

    except ValueError as e:
        logger.warning("Validación creando registros masivos de domicilio | error=%s", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except HTTPException:
        raise

    except Exception:
        logger.exception("Error inesperado creando registros masivos de domicilio.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear los registros de domicilios.")

@router.put("/{IdDeliveryRecord}", response_model=apiResponseDto[DeliveryRecordResponseDto])
def updateDeliveryRecord(IdDeliveryRecord: int, deliveryData: DeliveryRecordUpdateDto, payload: dict = Depends(getCurrentPayload), service: IDeliveryRecordApplication = Depends(getDeliveryRecordApplication)):
    try:
        userId = getAuthenticatedUserId(payload)
        logger.info("Actualizando registro de domicilio | IdDeliveryRecord=%s | userId=%s", IdDeliveryRecord, userId)
        data = service.update(IdDeliveryRecord, deliveryData, userId)
        logger.info("Registro de domicilio actualizado correctamente | IdDeliveryRecord=%s | userId=%s", IdDeliveryRecord, userId)
        return apiResponseDto(isSuccess=True, Message="Registro de domicilio actualizado correctamente.", result=data)

    except ValueError as e:
        message = str(e)

        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )

        logger.warning("Validación actualizando registro de domicilio | IdDeliveryRecord=%s | status=%s | error=%s", IdDeliveryRecord, statusCode, message)

        raise HTTPException(status_code=statusCode, detail=message)

    except HTTPException:
        raise

    except Exception:
        logger.exception("Error inesperado actualizando registro de domicilio | IdDeliveryRecord=%s", IdDeliveryRecord)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro de domicilio.")

@router.delete("/{IdDeliveryRecord}", response_model=apiResponseDto[dict])
def deleteDeliveryRecord(IdDeliveryRecord: int, payload: dict = Depends(getCurrentPayload), service: IDeliveryRecordApplication = Depends(getDeliveryRecordApplication)):
    try:
        logger.info("Eliminando registro de domicilio | IdDeliveryRecord=%s", IdDeliveryRecord)
        service.delete(IdDeliveryRecord)
        logger.info("Registro de domicilio eliminado correctamente | IdDeliveryRecord=%s", IdDeliveryRecord)
        return apiResponseDto(isSuccess=True, Message="Registro de domicilio eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("Registro de domicilio no encontrado al eliminar | IdDeliveryRecord=%s | error=%s", IdDeliveryRecord, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.exception("Error inesperado eliminando registro de domicilio | IdDeliveryRecord=%s", IdDeliveryRecord)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro de domicilio.")