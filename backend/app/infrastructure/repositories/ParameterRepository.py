from app.domain.dtos.ParameterDto import ParameterCreateDto, ParameterUpdateDto
from app.domain.interfaces.IParameterRepository import IParameterRepository
from app.domain.entities.ParameterHistory import ParameterHistory
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.domain.entities.Parameter import Parameter
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from typing import List, Optional

class ParameterRepository(IParameterRepository):

    def __init__(self, db: Session):
        self.db = db

    def _nowBogota(self) -> datetime:
        colombiaTimezone = timezone(timedelta(hours=-5))
        return datetime.now(colombiaTimezone).replace(tzinfo=None)

    def getAll(self) -> List[Parameter]:
        return (self.db.query(Parameter).order_by(Parameter.IdParameter.asc()).all())

    def getById(self, IdParameter: int) -> Optional[Parameter]:
        return (self.db.query(Parameter).filter(Parameter.IdParameter == IdParameter).first())

    def getByName(self, nameParameter: str) -> Optional[Parameter]:
        return (self.db.query(Parameter).filter(Parameter.nameParameter == nameParameter.strip()).first())
    
    def getHistoryByParameterId(self, IdParameter: int) -> List[ParameterHistory]:
        return (self.db.query(ParameterHistory).filter(ParameterHistory.IdParameter == IdParameter).order_by(ParameterHistory.createdAtParameterHistory.desc()).all())

    def create(self, parameterData: ParameterCreateDto, userLogin: str) -> Parameter:
        try:
            newParameter = Parameter(
                nameParameter=parameterData.nameParameter.strip(),
                valueParameter=parameterData.valueParameter.strip(),
                createdByParameter=userLogin,
                createdAtParameter=self._nowBogota(),
                updatedByParameter=None,
                updatedAtParameter=None
            )
            self.db.add(newParameter)
            self.db.flush()
            parameterHistory = ParameterHistory(
                IdParameter=newParameter.IdParameter,
                actionParameterHistory="CREATED",
                previousNameParameter=None,
                newNameParameter=newParameter.nameParameter,
                previousValueParameter=None,
                newValueParameter=newParameter.valueParameter,
                createdByParameterHistory=userLogin,
                createdAtParameterHistory=self._nowBogota(),
            )
            self.db.add(parameterHistory)
            self.db.commit()
            self.db.refresh(newParameter)
            return newParameter

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un parámetro con ese nombre.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear el parámetro: {str(e)}")

    def update(self, IdParameter: int, parameterData: ParameterUpdateDto, userLogin: str) -> Optional[Parameter]:
        try:
            parameterFound = self.getById(IdParameter)

            if not parameterFound:
                return None

            previousNameParameter = parameterFound.nameParameter
            previousValueParameter = parameterFound.valueParameter
            newNameParameter = previousNameParameter
            newValueParameter = previousValueParameter

            if parameterData.nameParameter is not None:
                newNameParameter = parameterData.nameParameter.strip()

            if parameterData.valueParameter is not None:
                newValueParameter = parameterData.valueParameter.strip()

            hasChanges = (previousNameParameter != newNameParameter or previousValueParameter != newValueParameter)

            if not hasChanges:
                return parameterFound

            now = self._nowBogota()

            parameterFound.nameParameter = newNameParameter
            parameterFound.valueParameter = newValueParameter
            parameterFound.updatedByParameter = userLogin
            parameterFound.updatedAtParameter = now

            parameterHistory = ParameterHistory(
                IdParameter=parameterFound.IdParameter,
                actionParameterHistory="UPDATED",
                previousNameParameter=previousNameParameter,
                newNameParameter=newNameParameter,
                previousValueParameter=previousValueParameter,
                newValueParameter=newValueParameter,
                createdByParameterHistory=userLogin,
                createdAtParameterHistory=now
            )

            self.db.add(parameterHistory)

            self.db.commit()
            self.db.refresh(parameterFound)

            return parameterFound

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un parámetro con ese nombre.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar el parámetro: {str(e)}")

    def delete(self, IdParameter: int) -> bool:
        try:
            parameterFound = self.getById(IdParameter)

            if not parameterFound:
                return False

            self.db.delete(parameterFound)
            self.db.commit()
            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar el parámetro: {str(e)}")