from app.infrastructure.repositories.AbsenceTypeRepository import AbsenceTypeRepository
from app.application.interfaces.IAbsenceTypeApplication import IAbsenceTypeApplication
from app.application.services.AbsenceTypeApplication import AbsenceTypeApplication
from app.domain.dtos.AbsenceTypeDto import AbsenceTypeResponseDto
from fastapi import APIRouter, Depends, HTTPException, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.api.authController import getCurrentPayload
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/absence-type", tags=["absence-type"])
logger = getLogger(__name__)

def getAbsenceTypeApplication(db: Session = Depends(getDb)) -> IAbsenceTypeApplication:
    absenceTypeRepository = AbsenceTypeRepository(db)
    return AbsenceTypeApplication(absenceTypeRepository)

@router.get("/", response_model=apiResponseDto[List[AbsenceTypeResponseDto]])
def getAllAbsenceTypes(payload: dict = Depends(getCurrentPayload), service: IAbsenceTypeApplication = Depends(getAbsenceTypeApplication)):
    try:
        logger.info("Consultando tipos de ausentismo")
        data = service.getAllActive()

        if not data:
            logger.info("No existen tipos de ausentismo activos")

            return apiResponseDto(isSuccess=False, Message="No existen tipos de ausentismo activos.", result=[])

        logger.info("Tipos de ausentismo obtenidos correctamente | total=%s", len(data))
        return apiResponseDto(isSuccess=True, Message="Tipos de ausentismo obtenidos correctamente.", result=data)

    except Exception:
        logger.exception("Error inesperado obteniendo tipos de ausentismo")

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los tipos de ausentismo.")