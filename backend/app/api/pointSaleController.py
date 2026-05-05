from app.domain.dtos.pointSaleDto import ( pointSaleCreateDto, pointSaleUpdateDto, pointSaleResponseDto )
from app.infrastructure.repositories.pointSaleRepository import pointSaleRepository
from app.application.services.pointSaleApplication import pointSaleApplication
from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/pointSale", tags=["pointSale"])

def getPointSaleApplication(db: Session = Depends(getDb)) -> pointSaleApplication:
    repository = pointSaleRepository(db)
    return pointSaleApplication(repository)

@router.get("/", response_model=apiResponseDto[List[pointSaleResponseDto]])
def getAllPointSale(service: pointSaleApplication = Depends(getPointSaleApplication)):
    try:
        data = service.getAll()
        if not data:
            return apiResponseDto(isSuccess=False, Message="No existen puntos de venta registrados.", result=[])
        return apiResponseDto(isSuccess=True, Message="Puntos de venta obtenidos correctamente.", result=data)
    
    except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los Puntos de Venta.")

@router.get("/{IdPointSale}", response_model=apiResponseDto[pointSaleResponseDto])
def getPointSaleById(IdPointSale: int, service: pointSaleApplication = Depends(getPointSaleApplication)):
    try:
        pointSaleFound = service.getById(IdPointSale)

        if not pointSaleFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto de Venta no encontrado.")

        return apiResponseDto(isSuccess=True, Message="Punto de venta obtenido correctamente.", result=pointSaleFound)
    
    except HTTPException:
            raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el Punto de Venta.")    

@router.post("/", response_model=apiResponseDto[pointSaleResponseDto], status_code=status.HTTP_201_CREATED)
def createPointSale(pointSaleData: pointSaleCreateDto, service: pointSaleApplication = Depends(getPointSaleApplication)):
    try:
        createdPointSale = service.create(pointSaleData)
        return apiResponseDto(isSuccess=True, Message="Punto de venta creado correctamente.", result=createdPointSale)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e),)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el Punto de Venta.",)

@router.put("/{IdPointSale}", response_model=apiResponseDto[pointSaleResponseDto])
def updatePointSale(IdPointSale: int, pointSaleData: pointSaleUpdateDto, service: pointSaleApplication = Depends(getPointSaleApplication)):
    try:
        pointSaleUpdated = service.update(IdPointSale, pointSaleData)

        if not pointSaleUpdated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto de Venta no encontrado.")

        return apiResponseDto(isSuccess=True, Message="Punto de venta actualizado correctamente.", result=pointSaleUpdated)
    
    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e),)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el Punto de Venta.",)

@router.delete("/{IdPointSale}", response_model=apiResponseDto[dict])
def deletePointSale(IdPointSale: int, service: pointSaleApplication = Depends(getPointSaleApplication)):
    try:
        deleted = service.delete(IdPointSale)

        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto de venta no encontrado.")

        return apiResponseDto(isSuccess=True, Message="Punto de venta eliminado correctamente.", result={})
    
    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el Punto de venta.",)