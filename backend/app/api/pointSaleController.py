from app.domain.dtos.pointSaleDto import ( pointSaleCreateDto, pointSaleUpdateDto, pointSaleResponseDto )
from app.infrastructure.repositories.pointSaleRepository import pointSaleRepository
from app.application.services.pointSaleApplication import pointSaleApplication
from app.infrastructure.logging.loggerConfig import getLogger
from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/pointSale", tags=["pointSale"])
logger = getLogger(__name__)

def getPointSaleApplication(db: Session = Depends(getDb)) -> pointSaleApplication:
    repository = pointSaleRepository(db)
    return pointSaleApplication(repository)

@router.get("/", response_model=apiResponseDto[List[pointSaleResponseDto]])
def getAllPointSale(service: pointSaleApplication = Depends(getPointSaleApplication)):
    try:
        logger.info("Consultando puntos de venta")
        data = service.getAll()

        if not data:
            logger.info("No existen puntos de venta registrados")
            return apiResponseDto(isSuccess=False, Message="No existen puntos de venta registrados.", result=[])
        
        logger.info("Puntos de venta obtenidos correctamente | total=%s", len(data))
        return apiResponseDto(isSuccess=True, Message="Puntos de venta obtenidos correctamente.", result=data)
    
    except Exception:
        logger.exception("Error inesperado obteniendo puntos de venta")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los Puntos de Venta.")

@router.get("/{IdPointSale}", response_model=apiResponseDto[pointSaleResponseDto])
def getPointSaleById(IdPointSale: int, service: pointSaleApplication = Depends(getPointSaleApplication)):
    try:
        logger.info("Consultando punto de venta por ID | IdPointSale=%s", IdPointSale)
        pointSaleFound = service.getById(IdPointSale)

        if not pointSaleFound:
            logger.warning("Punto de venta no encontrado | IdPointSale=%s", IdPointSale)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto de Venta no encontrado.")

        logger.info("Punto de venta obtenido correctamente | IdPointSale=%s", IdPointSale)
        return apiResponseDto(isSuccess=True, Message="Punto de venta obtenido correctamente.", result=pointSaleFound)
    
    except HTTPException:
            raise

    except Exception:
        logger.exception("Error inesperado obteniendo punto de venta | IdPointSale=%s", IdPointSale)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el Punto de Venta.")    

@router.post("/", response_model=apiResponseDto[pointSaleResponseDto], status_code=status.HTTP_201_CREATED)
def createPointSale(pointSaleData: pointSaleCreateDto, service: pointSaleApplication = Depends(getPointSaleApplication)):
    try:
        logger.info("Creando punto de venta | codePointSale=%s | namePointSale=%s", getattr(pointSaleData, "codePointSale", None), getattr(pointSaleData, "namePointSale", None))
        createdPointSale = service.create(pointSaleData)
        logger.info("Punto de venta creado correctamente | IdPointSale=%s | codePointSale=%s", getattr(createdPointSale, "IdPointSale", None), getattr(createdPointSale, "codePointSale", None))
        return apiResponseDto(isSuccess=True, Message="Punto de venta creado correctamente.", result=createdPointSale)
    
    except ValueError as e:
        logger.warning("Validación fallida creando punto de venta | codePointSale=%s | namePointSale=%s | error=%s", getattr(pointSaleData, "codePointSale", None), getattr(pointSaleData, "namePointSale", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e),)

    except Exception:
        logger.exception("Error inesperado creando punto de venta | codePointSale=%s | namePointSale=%s", getattr(pointSaleData, "codePointSale", None), getattr(pointSaleData, "namePointSale", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el Punto de Venta.",)

@router.put("/{IdPointSale}", response_model=apiResponseDto[pointSaleResponseDto])
def updatePointSale(IdPointSale: int, pointSaleData: pointSaleUpdateDto, service: pointSaleApplication = Depends(getPointSaleApplication)):
    try:
        logger.info("Actualizando punto de venta | IdPointSale=%s | codePointSale=%s | namePointSale=%s", IdPointSale, getattr(pointSaleData, "codePointSale", None), getattr(pointSaleData, "namePointSale", None))
        pointSaleUpdated = service.update(IdPointSale, pointSaleData)

        if not pointSaleUpdated:
            logger.warning("Punto de venta no encontrado al actualizar | IdPointSale=%s", IdPointSale)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto de Venta no encontrado.")

        logger.info("Punto de venta actualizado correctamente | IdPointSale=%s", IdPointSale)
        return apiResponseDto(isSuccess=True, Message="Punto de venta actualizado correctamente.", result=pointSaleUpdated)
    
    except HTTPException:
        raise

    except ValueError as e:
        logger.warning("Validación fallida actualizando punto de venta | IdPointSale=%s | error=%s", IdPointSale, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e),)

    except Exception:
        logger.exception("Error inesperado actualizando punto de venta | IdPointSale=%s", IdPointSale)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el Punto de Venta.",)

@router.delete("/{IdPointSale}", response_model=apiResponseDto[dict])
def deletePointSale(IdPointSale: int, service: pointSaleApplication = Depends(getPointSaleApplication)):
    try:
        logger.info("Eliminando punto de venta | IdPointSale=%s", IdPointSale)
        deleted = service.delete(IdPointSale)

        if not deleted:
            logger.warning("Punto de venta no encontrado al eliminar | IdPointSale=%s", IdPointSale)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto de venta no encontrado.")

        logger.info("Punto de venta eliminado correctamente | IdPointSale=%s", IdPointSale)
        return apiResponseDto(isSuccess=True, Message="Punto de venta eliminado correctamente.", result={})
    
    except HTTPException:
        raise

    except Exception:
        logger.exception("Error inesperado eliminando punto de venta | IdPointSale=%s", IdPointSale)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el Punto de venta.",)