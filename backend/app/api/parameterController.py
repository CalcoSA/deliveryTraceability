from app.domain.dtos.ParameterDto import (ParameterCreateDto, ParameterUpdateDto, ParameterResponseDto)
from app.infrastructure.repositories.ParameterRepository import ParameterRepository
from app.application.interfaces.IParameterApplication import IParameterApplication
from app.application.services.ParameterApplication import ParameterApplication
from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.api.authController import getCurrentPayload
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/parameter", tags=["parameter"])

def getParameterApplication(db: Session = Depends(getDb)) -> IParameterApplication:
    parameterRepository = ParameterRepository(db)
    return ParameterApplication(parameterRepository)

def getAuthenticatedUserLogin(payload: dict) -> str:
    userLogin = payload.get("wordpressUserLogin")

    if not userLogin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo identificar el usuario autenticado.")

    return userLogin

@router.get("/", response_model=apiResponseDto[List[ParameterResponseDto]])
def getAllParameters(payload: dict = Depends(getCurrentPayload), service: IParameterApplication = Depends(getParameterApplication)):
    try:
        data = service.getAll()

        if not data:
            return apiResponseDto(isSuccess=False, Message="No existen parámetros registrados.", result=[])

        return apiResponseDto(isSuccess=True, Message="Parámetros obtenidos correctamente.", result=data)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los parámetros.")


@router.get("/{IdParameter}", response_model=apiResponseDto[ParameterResponseDto])
def getParameterById(IdParameter: int, payload: dict = Depends(getCurrentPayload), service: IParameterApplication = Depends(getParameterApplication)):
    try:
        data = service.getById(IdParameter)

        return apiResponseDto(isSuccess=True, Message="Parámetro obtenido correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el parámetro.")


@router.post("/", response_model=apiResponseDto[ParameterResponseDto], status_code=status.HTTP_201_CREATED)
def createParameter(parameterData: ParameterCreateDto, payload: dict = Depends(getCurrentPayload), service: IParameterApplication = Depends(getParameterApplication)):
    try:
        userLogin = getAuthenticatedUserLogin(payload)
        data = service.create(parameterData, userLogin)
        return apiResponseDto(isSuccess=True, Message="Parámetro creado correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        print("ERROR REAL CREANDO PARAMETRO:", repr(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear el parámetro: {str(e)}")


@router.put("/{IdParameter}", response_model=apiResponseDto[ParameterResponseDto])
def updateParameter(IdParameter: int, parameterData: ParameterUpdateDto, payload: dict = Depends(getCurrentPayload), service: IParameterApplication = Depends(getParameterApplication)):
    try:
        userLogin = getAuthenticatedUserLogin(payload)
        data = service.update(IdParameter, parameterData, userLogin)
        return apiResponseDto(isSuccess=True, Message="Parámetro actualizado correctamente.", result=data)

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

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el parámetro.")


@router.delete("/{IdParameter}", response_model=apiResponseDto[dict])
def deleteParameter(IdParameter: int, payload: dict = Depends(getCurrentPayload), service: IParameterApplication = Depends(getParameterApplication)):
    try:
        service.delete(IdParameter)
        return apiResponseDto(isSuccess=True, Message="Parámetro eliminado correctamente.", result={})

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el parámetro.")