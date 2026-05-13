from app.domain.dtos.PointSaleEmailDto import (PointSaleEmailCreateDto, PointSaleEmailUpdateDto, PointSaleEmailResponseDto)
from app.infrastructure.repositories.PointSaleEmailRepository import PointSaleEmailRepository
from app.application.interfaces.IPointSaleEmailApplication import IPointSaleEmailApplication
from app.application.services.PointSaleEmailApplication import PointSaleEmailApplication
from fastapi import APIRouter, Depends, HTTPException, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.api.authController import getCurrentPayload
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/point-sale-email", tags=["point-sale-email"])
logger = getLogger(__name__)

def getPointSaleEmailApplication(db: Session = Depends(getDb)) -> IPointSaleEmailApplication:
    repository = PointSaleEmailRepository(db)
    return PointSaleEmailApplication(repository)

@router.get("/", response_model=apiResponseDto[List[PointSaleEmailResponseDto]])
def getAllPointSaleEmails(payload: dict = Depends(getCurrentPayload), service: IPointSaleEmailApplication = Depends(getPointSaleEmailApplication)):
    try:
        data = service.getAll()
        return apiResponseDto(isSuccess=True, Message="Correos de punto de venta obtenidos correctamente.", result=data)

    except Exception:
        logger.exception("Error inesperado obteniendo correos de punto de venta")

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los correos de punto de venta.")

@router.post("/", response_model=apiResponseDto[PointSaleEmailResponseDto], status_code=status.HTTP_201_CREATED)
def createPointSaleEmail(data: PointSaleEmailCreateDto, payload: dict = Depends(getCurrentPayload), service: IPointSaleEmailApplication = Depends(getPointSaleEmailApplication)):
    try:
        result = service.create(data)
        return apiResponseDto(isSuccess=True, Message="Correo de punto de venta creado correctamente.", result=result)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando correo de punto de venta")

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el correo de punto de venta.")

@router.put("/{IdPointSaleEmail}", response_model=apiResponseDto[PointSaleEmailResponseDto])
def updatePointSaleEmail(IdPointSaleEmail: int, data: PointSaleEmailUpdateDto, payload: dict = Depends(getCurrentPayload), service: IPointSaleEmailApplication = Depends(getPointSaleEmailApplication)):
    try:
        result = service.update(IdPointSaleEmail, data)
        return apiResponseDto(isSuccess=True, Message="Correo de punto de venta actualizado correctamente.", result=result)

    except ValueError as e:
        message = str(e)

        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando correo de punto de venta | IdPointSaleEmail=%s", IdPointSaleEmail)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el correo de punto de venta.")


@router.delete("/{IdPointSaleEmail}", response_model=apiResponseDto[dict])
def deletePointSaleEmail(IdPointSaleEmail: int, payload: dict = Depends(getCurrentPayload), service: IPointSaleEmailApplication = Depends(getPointSaleEmailApplication)):
    try:
        service.delete(IdPointSaleEmail)
        return apiResponseDto(isSuccess=True, Message="Correo de punto de venta eliminado correctamente.", result={})

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando correo de punto de venta | IdPointSaleEmail=%s", IdPointSaleEmail)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el correo de punto de venta.")