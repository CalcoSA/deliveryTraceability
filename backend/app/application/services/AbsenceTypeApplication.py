from app.application.interfaces.IAbsenceTypeApplication import IAbsenceTypeApplication
from app.domain.interfaces.IAbsenceTypeRepository import IAbsenceTypeRepository
from app.domain.entities.AbsenceType import AbsenceType
from typing import List

class AbsenceTypeApplication(IAbsenceTypeApplication):

    def __init__(self, absenceTypeRepository: IAbsenceTypeRepository):
        self.absenceTypeRepository = absenceTypeRepository

    def getAllActive(self) -> List[AbsenceType]:
        return self.absenceTypeRepository.getAllActive()