from app.domain.dtos.DomiciliaryDto import ( DomiciliaryCreateDto, DomiciliaryUpdateDto, DomiciliaryResponseDto )
from app.infrastructure.repositories.DomiciliaryRepository import DomiciliaryRepository
from app.infrastructure.repositories.pointSaleRepository import pointSaleRepository
from app.application.services.DomiciliaryApplication import DomiciliaryApplication
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(prefix="/domiciliary", tags=["domiciliary"])

def getDomiciliaryApplication(db: Session = Depends(getDb)) -> DomiciliaryApplication:
    domiciliaryRepo = DomiciliaryRepository(db)
    pointSaleRepo = pointSaleRepository(db)
    return DomiciliaryApplication(domiciliaryRepo, pointSaleRepo)

@router.get("/", response_model=apiResponseDto[List[DomiciliaryResponseDto]])
def getAllDomiciliary(pointSale: Optional[int] = Query(None), statusDomiciliary: Optional[bool] = Query(None),service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        data = service.getAll(pointSale, statusDomiciliary)
        if not data:
            return apiResponseDto(isSuccess=False, Message="No existen domiciliarios registrados.", result=[])
        return apiResponseDto(isSuccess=True, Message="Domiciliarios obtenidos correctamente.", result=data)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los domiciliarios.")

@router.get("/{IdDomiciliary}", response_model=apiResponseDto[DomiciliaryResponseDto])
def getDomiciliaryById(IdDomiciliary: int, service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        data = service.getById(IdDomiciliary)
        return apiResponseDto(isSuccess=True, Message="Domiciliario obtenido correctamente.", result=data)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el domiciliario.")
    
@router.get("/document/{documentDomiciliary}", response_model=apiResponseDto[DomiciliaryResponseDto])
def getDomiciliaryByDocument(documentDomiciliary: str, service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        data = service.getByDocument(documentDomiciliary)
        return apiResponseDto(isSuccess=True, Message="Domiciliario obtenido correctamente.", result=data)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el domiciliario por documento.")
    
@router.get("/pointSale/{IdPointSale}", response_model=apiResponseDto[List[DomiciliaryResponseDto]])
def getDomiciliaryByPointSale(IdPointSale: int, service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        data = service.getByPointSale(IdPointSale)

        if not data:
            return apiResponseDto(isSuccess=False, Message="No existen domiciliarios registrados para este punto de venta.", result=[])
        return apiResponseDto(isSuccess=True, Message="Domiciliarios del punto de venta obtenidos correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los domiciliarios del punto de venta.")

@router.post("/", response_model=apiResponseDto[DomiciliaryResponseDto], status_code=status.HTTP_201_CREATED)
def createDomiciliary(domiciliaryData: DomiciliaryCreateDto, service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        data = service.create(domiciliaryData)
        return apiResponseDto(isSuccess=True, Message="Domiciliario creado correctamente.", result=data)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el domiciliario.")


@router.put("/{IdDomiciliary}", response_model=apiResponseDto[DomiciliaryResponseDto])
def updateDomiciliary(IdDomiciliary: int, domiciliaryData: DomiciliaryUpdateDto, service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        data = service.update(IdDomiciliary, domiciliaryData)
        return apiResponseDto(isSuccess=True, Message="Domiciliario actualizado correctamente.", result=data)
    
    except ValueError as e:
        message = str(e)
        statusCode = status.HTTP_404_NOT_FOUND if "no encontrado" in message.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=statusCode, detail=message)
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el domiciliario.")

@router.delete("/{IdDomiciliary}", response_model=apiResponseDto[dict])
def deleteDomiciliary(IdDomiciliary: int, service: DomiciliaryApplication = Depends(getDomiciliaryApplication)):
    try:
        service.delete(IdDomiciliary)
        return apiResponseDto(isSuccess=True, Message="Domiciliario eliminado correctamente.", result={})
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el domiciliario.")