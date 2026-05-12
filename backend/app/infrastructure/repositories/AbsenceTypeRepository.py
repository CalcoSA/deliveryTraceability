from app.domain.interfaces.IAbsenceTypeRepository import IAbsenceTypeRepository
from app.domain.entities.AbsenceType import AbsenceType
from sqlalchemy.orm import Session
from typing import List, Optional

class AbsenceTypeRepository(IAbsenceTypeRepository):

    def __init__(self, db: Session):
        self.db = db

    def getAllActive(self) -> List[AbsenceType]:
        return (self.db.query(AbsenceType).filter(AbsenceType.statusAbsenceType == True).order_by(AbsenceType.IdAbsenceType.asc()).all())

    def getById(self, IdAbsenceType: int) -> Optional[AbsenceType]:
        return (self.db.query(AbsenceType).filter(AbsenceType.IdAbsenceType == IdAbsenceType).first())