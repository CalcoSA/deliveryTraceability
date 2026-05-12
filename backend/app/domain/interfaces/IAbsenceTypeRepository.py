from app.domain.entities.AbsenceType import AbsenceType
from abc import ABC, abstractmethod
from typing import List, Optional

class IAbsenceTypeRepository(ABC):

    @abstractmethod
    def getAllActive(self) -> List[AbsenceType]:
        pass

    @abstractmethod
    def getById(self, IdAbsenceType: int) -> Optional[AbsenceType]:
        pass