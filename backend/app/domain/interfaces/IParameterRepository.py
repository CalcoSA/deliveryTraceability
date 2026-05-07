from app.domain.dtos.ParameterDto import ParameterCreateDto, ParameterUpdateDto
from app.domain.entities.Parameter import Parameter
from abc import ABC, abstractmethod
from typing import List, Optional

class IParameterRepository(ABC):

    @abstractmethod
    def getAll(self) -> List[Parameter]:
        pass

    @abstractmethod
    def getById(self, IdParameter: int) -> Optional[Parameter]:
        pass

    @abstractmethod
    def getByName(self, nameParameter: str) -> Optional[Parameter]:
        pass

    @abstractmethod
    def create(self, parameterData: ParameterCreateDto, userLogin: str) -> Parameter:
        pass

    @abstractmethod
    def update(self, IdParameter: int, parameterData: ParameterUpdateDto, userLogin: str) -> Optional[Parameter]:
        pass

    @abstractmethod
    def delete(self, IdParameter: int) -> bool:
        pass