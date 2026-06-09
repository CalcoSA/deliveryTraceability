from app.application.interfaces.IParameterApplication import IParameterApplication
from app.domain.dtos.ParameterDto import ParameterCreateDto, ParameterUpdateDto
from app.domain.interfaces.IParameterRepository import IParameterRepository
from app.domain.entities.Parameter import Parameter
from typing import List

class ParameterApplication(IParameterApplication):

    def __init__(self, parameterRepository: IParameterRepository):
        self.parameterRepository = parameterRepository

    def getAll(self) -> List[Parameter]:
        return self.parameterRepository.getAll()

    def getById(self, IdParameter: int) -> Parameter:
        parameterFound = self.parameterRepository.getById(IdParameter)

        if not parameterFound:
            raise ValueError("Parámetro no encontrado.")

        return parameterFound
    
    def getHistoryByParameterId(self, IdParameter: int):
        parameterFound = self.parameterRepository.getById(IdParameter)

        if not parameterFound:
            raise ValueError("Parámetro no encontrado.")

        return self.parameterRepository.getHistoryByParameterId(IdParameter)

    def create(self, parameterData: ParameterCreateDto, userLogin: str) -> Parameter:
        nameParameter = parameterData.nameParameter.strip()
        valueParameter = parameterData.valueParameter.strip()

        if not nameParameter:
            raise ValueError("El nombre del parámetro es obligatorio.")

        if not valueParameter:
            raise ValueError("El valor del parámetro es obligatorio.")

        parameterExists = self.parameterRepository.getByName(nameParameter)

        if parameterExists:
            raise ValueError("Ya existe un parámetro con ese nombre.")

        parameterData.nameParameter = nameParameter
        parameterData.valueParameter = valueParameter

        return self.parameterRepository.create(parameterData, userLogin)

    def update(self, IdParameter: int, parameterData: ParameterUpdateDto, userLogin: str) -> Parameter:
        parameterFound = self.parameterRepository.getById(IdParameter)

        if not parameterFound:
            raise ValueError("Parámetro no encontrado.")

        if parameterData.nameParameter is not None:
            nameParameter = parameterData.nameParameter.strip()

            if not nameParameter:
                raise ValueError("El nombre del parámetro es obligatorio.")

            parameterExists = self.parameterRepository.getByName(nameParameter)

            if parameterExists and parameterExists.IdParameter != IdParameter:
                raise ValueError("Ya existe un parámetro con ese nombre.")

            parameterData.nameParameter = nameParameter

        if parameterData.valueParameter is not None:
            valueParameter = parameterData.valueParameter.strip()

            if not valueParameter:
                raise ValueError("El valor del parámetro es obligatorio.")

            parameterData.valueParameter = valueParameter

        parameterUpdated = self.parameterRepository.update(IdParameter, parameterData, userLogin)

        if not parameterUpdated:
            raise ValueError("Parámetro no encontrado.")

        return parameterUpdated

    def delete(self, IdParameter: int) -> bool:
        parameterFound = self.parameterRepository.getById(IdParameter)

        if not parameterFound:
            raise ValueError("Parámetro no encontrado.")

        return self.parameterRepository.delete(IdParameter)