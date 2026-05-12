from app.domain.dtos.ParameterDto import (ParameterCreateDto, ParameterUpdateDto, ParameterResponseDto, ParameterHistoryResponseDto)
from app.infrastructure.repositories.ParameterRepository import ParameterRepository
from app.application.interfaces.IParameterApplication import IParameterApplication
from app.application.services.ParameterApplication import ParameterApplication
from app.infrastructure.logging.loggerConfig import getLogger
from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.api.authController import getCurrentPayload
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/parameter", tags=["parameter"])
logger = getLogger(__name__)

def getParameterApplication(db: Session = Depends(getDb)) -> IParameterApplication:
    parameterRepository = ParameterRepository(db)
    return ParameterApplication(parameterRepository)

def getAuthenticatedUserLogin(payload: dict) -> str:
    userLogin = payload.get("wordpressUserLogin")

    if not userLogin:
        logger.warning("No se pudo identificar el usuario autenticado en el payload.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo identificar el usuario autenticado.")

    return userLogin

@router.get("/", response_model=apiResponseDto[List[ParameterResponseDto]])
def getAllParameters(payload: dict = Depends(getCurrentPayload), service: IParameterApplication = Depends(getParameterApplication)):
    try:
        logger.info("Consultando parámetros")
        data = service.getAll()

        if not data:
            logger.info("No existen parámetros registrados.")
            return apiResponseDto(isSuccess=False, Message="No existen parámetros registrados.", result=[])
        logger.info("Parámetros obtenidos correctamente | total=%s", len(data))
        return apiResponseDto(isSuccess=True, Message="Parámetros obtenidos correctamente.", result=data)

    except Exception:
        logger.exception("Error inesperado obteniendo parámetros.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los parámetros.")


@router.get("/{IdParameter}", response_model=apiResponseDto[ParameterResponseDto])
def getParameterById(IdParameter: int, payload: dict = Depends(getCurrentPayload), service: IParameterApplication = Depends(getParameterApplication)):
    try:
        logger.info("Consultando parámetro | IdParameter=%s", IdParameter)
        data = service.getById(IdParameter)
        logger.info("Parámetro obtenido correctamente | IdParameter=%s", IdParameter)
        return apiResponseDto(isSuccess=True, Message="Parámetro obtenido correctamente.", result=data)

    except ValueError as e:
        logger.warning("Parámetro no encontrado | IdParameter=%s | error=%s", IdParameter, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo parámetro | IdParameter=%s", IdParameter)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el parámetro.")
    
@router.get("/{IdParameter}/history", response_model=apiResponseDto[List[ParameterHistoryResponseDto]])
def getParameterHistory(IdParameter: int, payload: dict = Depends(getCurrentPayload), service: IParameterApplication = Depends(getParameterApplication)):
    try:
        logger.info("Consultando parámetro | IdParameter=%s", IdParameter)
        data = service.getHistoryByParameterId(IdParameter)

        if not data:
            logger.info("No existe historial para el parámetro | IdParameter=%s", IdParameter)
            return apiResponseDto(isSuccess=False, Message="No existe historial para este parámetro.", result=[])

        logger.info("Historial del parámetro obtenido correctamente | IdParameter=%s | total=%s", IdParameter, len(data))
        return apiResponseDto(isSuccess=True, Message="Historial del parámetro obtenido correctamente.", result=data)

    except ValueError as e:
        logger.warning("Parámetro no encontrado al consultar historial | IdParameter=%s | error=%s", IdParameter, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo historial del parámetro | IdParameter=%s", IdParameter)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el historial del parámetro.")

@router.post("/", response_model=apiResponseDto[ParameterResponseDto], status_code=status.HTTP_201_CREATED)
def createParameter(parameterData: ParameterCreateDto, payload: dict = Depends(getCurrentPayload), service: IParameterApplication = Depends(getParameterApplication)):
    try:
        userLogin = getAuthenticatedUserLogin(payload)
        logger.info("Creando parámetro | nameParameter=%s | userLogin=%s", getattr(parameterData, "nameParameter", None), userLogin)
        data = service.create(parameterData, userLogin)
        logger.info("Parámetro creado correctamente | IdParameter=%s | nameParameter=%s | userLogin=%s", getattr(data, "IdParameter", None), getattr(data, "nameParameter", None), userLogin)
        return apiResponseDto(isSuccess=True, Message="Parámetro creado correctamente.", result=data)

    except ValueError as e:
        logger.warning("Validación creando parámetro | nameParameter=%s | error=%s", getattr(parameterData, "nameParameter", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Error inesperado creando parámetro | nameParameter=%s", getattr(parameterData, "nameParameter", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear el parámetro: {str(e)}")

@router.put("/{IdParameter}", response_model=apiResponseDto[ParameterResponseDto])
def updateParameter(IdParameter: int, parameterData: ParameterUpdateDto, payload: dict = Depends(getCurrentPayload), service: IParameterApplication = Depends(getParameterApplication)):
    try:
        userLogin = getAuthenticatedUserLogin(payload)
        logger.info("Actualizando parámetro | IdParameter=%s | nameParameter=%s | userLogin=%s", IdParameter, getattr(parameterData, "nameParameter", None), userLogin)
        data = service.update(IdParameter, parameterData, userLogin)
        logger.info("Parámetro actualizado correctamente | IdParameter=%s | userLogin=%s", IdParameter, userLogin)
        return apiResponseDto(isSuccess=True, Message="Parámetro actualizado correctamente.", result=data)

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )

        logger.warning("Validación actualizando parámetro | IdParameter=%s | status=%s | error=%s", IdParameter, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except HTTPException:
        raise

    except Exception:
        logger.exception("Error inesperado actualizando parámetro | IdParameter=%s", IdParameter)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el parámetro.")


@router.delete("/{IdParameter}", response_model=apiResponseDto[dict])
def deleteParameter(IdParameter: int, payload: dict = Depends(getCurrentPayload), service: IParameterApplication = Depends(getParameterApplication)):
    try:
        logger.info("Eliminando parámetro | IdParameter=%s", IdParameter)
        service.delete(IdParameter)
        logger.info("Parámetro eliminado correctamente | IdParameter=%s", IdParameter)
        return apiResponseDto(isSuccess=True, Message="Parámetro eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("Parámetro no encontrado al eliminar | IdParameter=%s | error=%s", IdParameter, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando parámetro | IdParameter=%s", IdParameter)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el parámetro.")