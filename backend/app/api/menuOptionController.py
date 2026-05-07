from app.domain.dtos.MenuOptionDto import ( MenuOptionCreateDto, MenuOptionUpdateDto, MenuOptionResponseDto )
from app.infrastructure.repositories.MenuOptionRepository import MenuOptionRepository
from app.application.interfaces.IMenuOptionApplication import IMenuOptionApplication
from app.application.services.MenuOptionApplication import MenuOptionApplication
from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/menu-option", tags=["menu-option"])

def getMenuOptionApplication(db: Session = Depends(getDb)) -> IMenuOptionApplication:
    repository = MenuOptionRepository(db)
    return MenuOptionApplication(repository)

@router.get("/", response_model=apiResponseDto[List[MenuOptionResponseDto]])
def getAllMenuOptions(service: IMenuOptionApplication = Depends(getMenuOptionApplication)):
    try:
        data = service.getAll()
        return apiResponseDto(isSuccess=True, Message="Opciones de menú obtenidas correctamente.", result=data)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener las opciones de menú.")

@router.get("/{IdMenuOption}", response_model=apiResponseDto[MenuOptionResponseDto])
def getMenuOptionById(IdMenuOption: int, service: IMenuOptionApplication = Depends(getMenuOptionApplication)):
    try:
        data = service.getById(IdMenuOption)
        return apiResponseDto(isSuccess=True, Message="Opción de menú obtenida correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la opción de menú.")


@router.post("/", response_model=apiResponseDto[MenuOptionResponseDto], status_code=status.HTTP_201_CREATED)
def createMenuOption(menuOptionData: MenuOptionCreateDto, service: IMenuOptionApplication = Depends(getMenuOptionApplication)):
    try:
        data = service.create(menuOptionData)
        return apiResponseDto(isSuccess=True, Message="Opción de menú creada correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear la opción de menú.")


@router.put("/{IdMenuOption}", response_model=apiResponseDto[MenuOptionResponseDto])
def updateMenuOption(IdMenuOption: int, menuOptionData: MenuOptionUpdateDto, service: IMenuOptionApplication = Depends(getMenuOptionApplication)):
    try:
        data = service.update(IdMenuOption, menuOptionData)
        return apiResponseDto(isSuccess=True, Message="Opción de menú actualizada correctamente.", result=data)

    except ValueError as e:
        message = str(e)
        statusCode = status.HTTP_404_NOT_FOUND if "no encontrada" in message.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar la opción de menú.")


@router.delete("/{IdMenuOption}", response_model=apiResponseDto[dict])
def deleteMenuOption(IdMenuOption: int, service: IMenuOptionApplication = Depends(getMenuOptionApplication)):
    try:
        service.delete(IdMenuOption)
        return apiResponseDto(isSuccess=True, Message="Opción de menú eliminada correctamente.", result={})

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar la opción de menú.")