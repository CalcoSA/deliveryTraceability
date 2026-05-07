from app.domain.dtos.DeliveryRecordDto import (DeliveryRecordCreateDto, DeliveryRecordUpdateDto, DeliveryRecordResponseDto, DeliveryRecordBulkCreateDto)
from app.infrastructure.repositories.DeliveryRecordRepository import DeliveryRecordRepository
from app.application.interfaces.IDeliveryRecordApplication import IDeliveryRecordApplication
from app.application.services.DeliveryRecordApplication import DeliveryRecordApplication
from app.infrastructure.repositories.DomiciliaryRepository import DomiciliaryRepository
from app.infrastructure.repositories.pointSaleRepository import pointSaleRepository
from app.infrastructure.repositories.ParameterRepository import ParameterRepository
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.api.authController import getCurrentPayload
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/delivery-record", tags=["delivery-record"])

def getDeliveryRecordApplication(db: Session = Depends(getDb)) -> IDeliveryRecordApplication:
    deliveryRecordRepository = DeliveryRecordRepository(db)
    pointSaleRepo = pointSaleRepository(db)
    domiciliaryRepo = DomiciliaryRepository(db)
    parameterRepo = ParameterRepository(db)

    return DeliveryRecordApplication(deliveryRecordRepository, pointSaleRepo, domiciliaryRepo, parameterRepo)

def getAuthenticatedUserId(payload: dict) -> int:
    userId = payload.get("wordpressUserId")

    if not userId:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo identificar el usuario autenticado.")

    return int(userId)

@router.get("/", response_model=apiResponseDto[List[DeliveryRecordResponseDto]])
def getAllDeliveryRecords(deliveryDate: Optional[date] = Query(None), IdPointSale: Optional[int] = Query(None), IdDomiciliary: Optional[int] = Query(None), payload: dict = Depends(getCurrentPayload), service: IDeliveryRecordApplication = Depends(getDeliveryRecordApplication)):
    try:
        data = service.getAll(deliveryDate, IdPointSale, IdDomiciliary)

        if not data:
            return apiResponseDto(isSuccess=False, Message="No existen registros de domicilios.", result=[])

        return apiResponseDto(isSuccess=True, Message="Registros de domicilios obtenidos correctamente.", result=data)

    except Exception as e:
        print("ERROR REAL OBTENIENDO REGISTROS DE DOMICILIOS:", repr(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros de domicilios.")

@router.get("/{IdDeliveryRecord}", response_model=apiResponseDto[DeliveryRecordResponseDto])
def getDeliveryRecordById(IdDeliveryRecord: int, payload: dict = Depends(getCurrentPayload), service: IDeliveryRecordApplication = Depends(getDeliveryRecordApplication)):
    try:
        data = service.getById(IdDeliveryRecord)
        return apiResponseDto(isSuccess=True, Message="Registro de domicilio obtenido correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        print("ERROR REAL OBTENIENDO REGISTRO DE DOMICILIO:", repr(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro de domicilio.")

@router.post("/", response_model=apiResponseDto[DeliveryRecordResponseDto], status_code=status.HTTP_201_CREATED)
def createDeliveryRecord(deliveryData: DeliveryRecordCreateDto, payload: dict = Depends(getCurrentPayload), service: IDeliveryRecordApplication = Depends(getDeliveryRecordApplication)):
    try:
        userId = getAuthenticatedUserId(payload)
        data = service.create(deliveryData, userId)
        return apiResponseDto(isSuccess=True, Message="Registro de domicilio creado correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        print("ERROR REAL CREANDO REGISTRO DE DOMICILIO:", repr(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro de domicilio.")
    
@router.post("/bulk", response_model=apiResponseDto[List[DeliveryRecordResponseDto]], status_code=status.HTTP_201_CREATED)
def createManyDeliveryRecords(deliveryData: DeliveryRecordBulkCreateDto, payload: dict = Depends(getCurrentPayload), service: IDeliveryRecordApplication = Depends(getDeliveryRecordApplication)):
    try:
        userId = getAuthenticatedUserId(payload)
        data = service.createMany(deliveryData, userId)
        return apiResponseDto(isSuccess=True, Message="Registros de domicilios creados correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        print("ERROR REAL CREANDO REGISTROS MASIVOS DE DOMICILIO:", repr(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear los registros de domicilios.")

@router.put("/{IdDeliveryRecord}", response_model=apiResponseDto[DeliveryRecordResponseDto])
def updateDeliveryRecord(IdDeliveryRecord: int, deliveryData: DeliveryRecordUpdateDto, payload: dict = Depends(getCurrentPayload), service: IDeliveryRecordApplication = Depends(getDeliveryRecordApplication)):
    try:
        userId = getAuthenticatedUserId(payload)
        data = service.update(IdDeliveryRecord, deliveryData, userId)

        return apiResponseDto(isSuccess=True, Message="Registro de domicilio actualizado correctamente.", result=data)

    except ValueError as e:
        message = str(e)

        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(status_code=statusCode, detail=message)

    except HTTPException:
        raise

    except Exception as e:
        print("ERROR REAL ACTUALIZANDO REGISTRO DE DOMICILIO:", repr(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro de domicilio.")

@router.delete("/{IdDeliveryRecord}", response_model=apiResponseDto[dict])
def deleteDeliveryRecord(IdDeliveryRecord: int, payload: dict = Depends(getCurrentPayload), service: IDeliveryRecordApplication = Depends(getDeliveryRecordApplication)):
    try:
        service.delete(IdDeliveryRecord)
        return apiResponseDto(isSuccess=True, Message="Registro de domicilio eliminado correctamente.", result={})

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        print("ERROR REAL ELIMINANDO REGISTRO DE DOMICILIO:", repr(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro de domicilio.")