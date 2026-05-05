from app.domain.dtos.pointSaleDto import pointSaleCreateDto, pointSaleUpdateDto
from app.domain.interfaces.IpointSaleRepository import IpointSaleRepository
from app.domain.entities.pointSale import pointSale
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

class pointSaleRepository(IpointSaleRepository):
    def __init__(self, db: Session):
        self.db = db

    def getAll(self) -> List[pointSale]:
        return self.db.query(pointSale).all()

    def getById(self, IdPointSale: int) -> Optional[pointSale]:
        return (self.db.query(pointSale).filter(pointSale.IdPointSale == IdPointSale).first())
    
    def getByCodeInsensitive(self, codePointSale: str) -> Optional[pointSale]:
        return (self.db.query(pointSale).filter(func.lower(pointSale.codePointSale) == codePointSale.strip().lower()).first())

    def create(self, pointSaleData: pointSaleCreateDto) -> pointSale:
        try:
            newPointSale = pointSale(codePointSale=pointSaleData.codePointSale, namePointSale=pointSaleData.namePointSale, statusPointSale=pointSaleData.statusPointSale)

            self.db.add(newPointSale)
            self.db.commit()
            self.db.refresh(newPointSale)
            return newPointSale
        
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update(self, IdPointSale: int, pointSaleData: pointSaleUpdateDto) -> Optional[pointSale]:
        pointSaleFound = self.getById(IdPointSale)

        if not pointSaleFound:
            return None

        if pointSaleData.codePointSale is not None:
            pointSaleFound.codePointSale = pointSaleData.codePointSale

        if pointSaleData.namePointSale is not None:
            pointSaleFound.namePointSale = pointSaleData.namePointSale

        if pointSaleData.statusPointSale is not None:
            pointSaleFound.statusPointSale = pointSaleData.statusPointSale

        try:
            self.db.commit()
            self.db.refresh(pointSaleFound)
            return pointSaleFound
        
        except SQLAlchemyError:
            self.db.rollback()
            raise


    def delete(self, IdPointSale: int) -> bool:
        pointSaleFound = self.getById(IdPointSale)

        if not pointSaleFound:
            return False

        try:
            self.db.delete(pointSaleFound)
            self.db.commit()
            return True
        
        except SQLAlchemyError:
                self.db.rollback()
                raise