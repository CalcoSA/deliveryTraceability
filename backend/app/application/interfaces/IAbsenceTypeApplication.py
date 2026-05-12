from app.domain.entities.AbsenceType import AbsenceType
from abc import ABC, abstractmethod
from typing import List

class IAbsenceTypeApplication(ABC):

    @abstractmethod
    def getAllActive(self) -> List[AbsenceType]:
        pass