from app.domain.interfaces.IPointSaleEmailRepository import IPointSaleEmailRepository
from app.domain.entities.PointSaleEmail import PointSaleEmail
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from typing import List, Optional

class PointSaleEmailRepository(IPointSaleEmailRepository):

    def __init__(self, db: Session):
        self.db = db

    def _nowBogota(self) -> datetime:
        colombiaTimezone = timezone(timedelta(hours=-5))
        return datetime.now(colombiaTimezone).replace(tzinfo=None)

    def _normalizeEmail(self, emailPointSale: str) -> str:
        return emailPointSale.strip().lower()

    def getAll(self) -> List[PointSaleEmail]:
        return (self.db.query(PointSaleEmail).order_by(PointSaleEmail.IdPointSaleEmail.asc()).all())

    def getById(self, IdPointSaleEmail: int) -> Optional[PointSaleEmail]:
        return (self.db.query(PointSaleEmail).filter(PointSaleEmail.IdPointSaleEmail == IdPointSaleEmail).first())

    def getByEmail(self, emailPointSale: str) -> Optional[PointSaleEmail]:
        return (self.db.query(PointSaleEmail).filter(PointSaleEmail.emailPointSale == self._normalizeEmail(emailPointSale)).first())

    def create(self, emailPointSale: str) -> PointSaleEmail:
        try:
            newEmail = PointSaleEmail(
                emailPointSale=self._normalizeEmail(emailPointSale),
                statusPointSaleEmail=True,
                createdAtPointSaleEmail=self._nowBogota(),
                updatedAtPointSaleEmail=None
            )

            self.db.add(newEmail)
            self.db.commit()
            self.db.refresh(newEmail)

            return newEmail

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un correo de punto de venta registrado.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear el correo de punto de venta: {str(e)}")

    def update(self, IdPointSaleEmail: int, emailPointSale: Optional[str], statusPointSaleEmail: Optional[bool]) -> Optional[PointSaleEmail]:
        try:
            emailFound = self.getById(IdPointSaleEmail)

            if not emailFound:
                return None

            if emailPointSale is not None:
                emailFound.emailPointSale = self._normalizeEmail(emailPointSale)

            if statusPointSaleEmail is not None:
                emailFound.statusPointSaleEmail = statusPointSaleEmail

            emailFound.updatedAtPointSaleEmail = self._nowBogota()

            self.db.commit()
            self.db.refresh(emailFound)

            return emailFound

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un correo de punto de venta registrado.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar el correo de punto de venta: {str(e)}")

    def delete(self, IdPointSaleEmail: int) -> bool:
        try:
            emailFound = self.getById(IdPointSaleEmail)

            if not emailFound:
                return False

            self.db.delete(emailFound)
            self.db.commit()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar el correo de punto de venta: {str(e)}")