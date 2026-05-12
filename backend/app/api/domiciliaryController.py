from app.domain.dtos.DomiciliaryDto import ( DomiciliaryCreateDto, DomiciliaryUpdateDto, DomiciliaryResponseDto )
from app.infrastructure.repositories.DomiciliaryRepository import DomiciliaryRepository
from app.infrastructure.repositories.pointSaleRepository import pointSaleRepository
from app.application.services.DomiciliaryApplication import DomiciliaryApplication
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(prefix="/domiciliary", tags=["domiciliary"])
logger = getLogger(__name__)

def getDomiciliaryApplication(db: Session = Depends(getDb)) -> DomiciliaryApplication:
    domiciliaryRepo = DomiciliaryRepository(db)
    pointSaleRepo = pointSaleRepository(db)
    return DomiciliaryApplication(domiciliaryRepo, pointSaleRepo)

@router.get("/", response_model=apiResponseDto[List[DomiciliaryResponseDto]])
def getAllDomiciliary(pointSale: Optional[int] = Query(None), statusDomiciliary: Optional[bool] = Query(None),service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        logger.info("Consultando domiciliarios | pointSale=%s | statusDomiciliary=%s", pointSale, statusDomiciliary)
        data = service.getAll(pointSale, statusDomiciliary)
        if not data:
            logger.info("No existen domiciliarios registrados para los filtros enviados.")
            return apiResponseDto(isSuccess=False, Message="No existen domiciliarios registrados.", result=[])
        logger.info("Domiciliarios obtenidos correctamente | total=%s", len(data))
        return apiResponseDto(isSuccess=True, Message="Domiciliarios obtenidos correctamente.", result=data)
    
    except ValueError as e:
        logger.warning("Validación consultando domiciliarios | pointSale=%s | statusDomiciliary=%s | error=%s", pointSale, statusDomiciliary, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo domiciliarios | pointSale=%s | statusDomiciliary=%s", pointSale, statusDomiciliary)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los domiciliarios.")

@router.get("/{IdDomiciliary}", response_model=apiResponseDto[DomiciliaryResponseDto])
def getDomiciliaryById(IdDomiciliary: int, service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        logger.info("Consultando domiciliario por ID | IdDomiciliary=%s", IdDomiciliary)
        data = service.getById(IdDomiciliary)
        logger.info("Domiciliario obtenido correctamente | IdDomiciliary=%s", IdDomiciliary)
        return apiResponseDto(isSuccess=True, Message="Domiciliario obtenido correctamente.", result=data)
    
    except ValueError as e:
        logger.warning("Domiciliario no encontrado | IdDomiciliary=%s | error=%s", IdDomiciliary, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception:
        logger.exception("Error inesperado obteniendo domiciliario | IdDomiciliary=%s", IdDomiciliary)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el domiciliario.")
    
@router.get("/document/{documentDomiciliary}", response_model=apiResponseDto[DomiciliaryResponseDto])
def getDomiciliaryByDocument(documentDomiciliary: str, service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        logger.info("Consultando domiciliario por documento | documentDomiciliary=%s", documentDomiciliary)
        data = service.getByDocument(documentDomiciliary)
        logger.info("Domiciliario obtenido por documento | documentDomiciliary=%s", documentDomiciliary)
        return apiResponseDto(isSuccess=True, Message="Domiciliario obtenido correctamente.", result=data)
    
    except ValueError as e:
        logger.warning("Domiciliario no encontrado por documento | documentDomiciliary=%s | error=%s", documentDomiciliary, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception:
        logger.exception("Error inesperado obteniendo domiciliario por documento | documentDomiciliary=%s", documentDomiciliary)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el domiciliario por documento.")
    
@router.get("/pointSale/{IdPointSale}", response_model=apiResponseDto[List[DomiciliaryResponseDto]])
def getDomiciliaryByPointSale(IdPointSale: int, service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        logger.info("Consultando domiciliarios por punto de venta | IdPointSale=%s", IdPointSale)
        data = service.getByPointSale(IdPointSale)

        if not data:
            logger.info("No existen domiciliarios para el punto de venta | IdPointSale=%s", IdPointSale)
            return apiResponseDto(isSuccess=False, Message="No existen domiciliarios registrados para este punto de venta.", result=[])
        logger.info("Domiciliarios del punto de venta obtenidos correctamente | IdPointSale=%s | total=%s", IdPointSale, len(data))
        return apiResponseDto(isSuccess=True, Message="Domiciliarios del punto de venta obtenidos correctamente.", result=data)

    except ValueError as e:
        logger.warning("Validación consultando domiciliarios por punto de venta | IdPointSale=%s | error=%s", IdPointSale, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo domiciliarios por punto de venta | IdPointSale=%s", IdPointSale)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los domiciliarios del punto de venta.")

@router.post("/", response_model=apiResponseDto[DomiciliaryResponseDto], status_code=status.HTTP_201_CREATED)
def createDomiciliary(domiciliaryData: DomiciliaryCreateDto, service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        logger.info("Creando domiciliario | documentDomiciliary=%s | nameDomiciliary=%s", getattr(domiciliaryData, "documentDomiciliary", None), getattr(domiciliaryData, "nameDomiciliary", None))
        data = service.create(domiciliaryData)
        logger.info("Domiciliario creado correctamente | IdDomiciliary=%s | documentDomiciliary=%s", getattr(data, "IdDomiciliary", None), getattr(data, "documentDomiciliary", None))
        return apiResponseDto(isSuccess=True, Message="Domiciliario creado correctamente.", result=data)
    
    except ValueError as e:
        logger.warning("Validación creando domiciliario | documentDomiciliary=%s | error=%s", getattr(domiciliaryData, "documentDomiciliary", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception:
        logger.exception("Error inesperado creando domiciliario | documentDomiciliary=%s", getattr(domiciliaryData, "documentDomiciliary", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el domiciliario.")


@router.put("/{IdDomiciliary}", response_model=apiResponseDto[DomiciliaryResponseDto])
def updateDomiciliary(IdDomiciliary: int, domiciliaryData: DomiciliaryUpdateDto, service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        logger.info("Actualizando domiciliario | IdDomiciliary=%s", IdDomiciliary)
        data = service.update(IdDomiciliary, domiciliaryData)
        logger.info("Domiciliario actualizado correctamente | IdDomiciliary=%s", IdDomiciliary)
        return apiResponseDto(isSuccess=True, Message="Domiciliario actualizado correctamente.", result=data)
    
    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando domiciliario | IdDomiciliary=%s | status=%s | error=%s", IdDomiciliary, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)
    
    except Exception:
        logger.exception("Error inesperado actualizando domiciliario | IdDomiciliary=%s", IdDomiciliary)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el domiciliario.")

@router.delete("/{IdDomiciliary}", response_model=apiResponseDto[dict])
def deleteDomiciliary(IdDomiciliary: int, service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        logger.info("Eliminando domiciliario | IdDomiciliary=%s", IdDomiciliary)
        service.delete(IdDomiciliary)
        logger.info("Domiciliario eliminado correctamente | IdDomiciliary=%s", IdDomiciliary)
        return apiResponseDto(isSuccess=True, Message="Domiciliario eliminado correctamente.", result={})
    
    except ValueError as e:
        logger.warning("Domiciliario no encontrado al eliminar | IdDomiciliary=%s | error=%s", IdDomiciliary, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception:
        logger.exception("Error inesperado eliminando domiciliario | IdDomiciliary=%s", IdDomiciliary)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el domiciliario.")