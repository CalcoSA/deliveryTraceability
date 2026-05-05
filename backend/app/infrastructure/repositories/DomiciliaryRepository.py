from app.domain.dtos.DomiciliaryDto import DomiciliaryCreateDto, DomiciliaryUpdateDto
from app.domain.interfaces.IDomiciliaryRepository import IDomiciliaryRepository
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.domain.entities.Domiciliary import Domiciliary
from sqlalchemy.orm import Session
from typing import List, Optional

class DomiciliaryRepository(IDomiciliaryRepository):
    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pointSale: Optional[int] = None, statusDomiciliary: Optional[bool] = None) -> List[Domiciliary]:
        query = self.db.query(Domiciliary)

        if pointSale is not None:
            query = query.filter(Domiciliary.pointSale == pointSale)

        if statusDomiciliary is not None:
            query = query.filter(Domiciliary.statusDomiciliary == statusDomiciliary)

        return query.all()

    def getById(self, IdDomiciliary: int) -> Optional[Domiciliary]:
        return (self.db.query(Domiciliary).filter(Domiciliary.IdDomiciliary == IdDomiciliary).first())

    def getByDocument(self, documentDomiciliary: str) -> Optional[Domiciliary]:
        return (self.db.query(Domiciliary).filter(Domiciliary.documentDomiciliary == documentDomiciliary).first())
    
    def getByPointSale(self, IdPointSale: int) -> List[Domiciliary]:
        return (self.db.query(Domiciliary).filter(Domiciliary.pointSale == IdPointSale).all())

    def create(self, domiciliaryData: DomiciliaryCreateDto) -> Domiciliary:
        try:
            newDomiciliary = Domiciliary(
                documentDomiciliary=domiciliaryData.documentDomiciliary.strip(),
                nameDomiciliary=domiciliaryData.nameDomiciliary,
                statusDomiciliary=domiciliaryData.statusDomiciliary,
                pointSale=domiciliaryData.pointSale
            )

            self.db.add(newDomiciliary)
            self.db.commit()
            self.db.refresh(newDomiciliary)
            return newDomiciliary

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un domiciliario con ese documento o el punto de venta no es válido.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear el domiciliario: {str(e)}")

    def update(self, IdDomiciliary: int, domiciliaryData: DomiciliaryUpdateDto) -> Optional[Domiciliary]:
        try:
            domiciliaryFound = self.getById(IdDomiciliary)

            if not domiciliaryFound:
                return None

            if domiciliaryData.documentDomiciliary is not None:
                domiciliaryFound.documentDomiciliary = domiciliaryData.documentDomiciliary.strip()

            if domiciliaryData.nameDomiciliary is not None:
                domiciliaryFound.nameDomiciliary = domiciliaryData.nameDomiciliary

            if domiciliaryData.statusDomiciliary is not None:
                domiciliaryFound.statusDomiciliary = domiciliaryData.statusDomiciliary

            if domiciliaryData.pointSale is not None:
                domiciliaryFound.pointSale = domiciliaryData.pointSale

            self.db.commit()
            self.db.refresh(domiciliaryFound)
            return domiciliaryFound

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un domiciliario con ese documento o el punto de venta no es válido.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar el domiciliario: {str(e)}")

    def delete(self, IdDomiciliary: int) -> bool:
        try:
            domiciliaryFound = self.getById(IdDomiciliary)

            if not domiciliaryFound:
                return False

            self.db.delete(domiciliaryFound)
            self.db.commit()
            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar el domiciliario: {str(e)}")