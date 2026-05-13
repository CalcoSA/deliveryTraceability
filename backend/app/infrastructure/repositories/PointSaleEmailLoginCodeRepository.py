from app.domain.entities.PointSaleEmailLoginCode import PointSaleEmailLoginCode
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

class PointSaleEmailLoginCodeRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, IdPointSaleEmail: int, codeHash: str, expiresAt: datetime, createdAt: datetime) -> PointSaleEmailLoginCode:
        try:
            newCode = PointSaleEmailLoginCode(
                IdPointSaleEmail=IdPointSaleEmail,
                codeHash=codeHash,
                attempts=0,
                expiresAt=expiresAt,
                usedAt=None,
                createdAt=createdAt
            )

            self.db.add(newCode)
            self.db.commit()
            self.db.refresh(newCode)

            return newCode

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear el código de acceso: {str(e)}")

    def invalidatePendingCodes(self, IdPointSaleEmail: int, usedAt: datetime) -> None:
        try:
            pendingCodes = (self.db.query(PointSaleEmailLoginCode).filter(PointSaleEmailLoginCode.IdPointSaleEmail == IdPointSaleEmail).filter(PointSaleEmailLoginCode.usedAt == None).all())

            for code in pendingCodes:
                code.usedAt = usedAt

            self.db.commit()

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al invalidar códigos anteriores: {str(e)}")

    def getLatestAvailableCode(self, IdPointSaleEmail: int, now: datetime) -> Optional[PointSaleEmailLoginCode]:
        return (self.db.query(PointSaleEmailLoginCode).filter(PointSaleEmailLoginCode.IdPointSaleEmail == IdPointSaleEmail).filter(PointSaleEmailLoginCode.usedAt == None).filter(PointSaleEmailLoginCode.expiresAt >= now).order_by(PointSaleEmailLoginCode.IdPointSaleEmailLoginCode.desc()).first())

    def increaseAttempts(self, code: PointSaleEmailLoginCode) -> None:
        try:
            code.attempts = code.attempts + 1
            self.db.commit()

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar intentos del código: {str(e)}")

    def markAsUsed(self, code: PointSaleEmailLoginCode, usedAt: datetime) -> None:
        try:
            code.usedAt = usedAt
            self.db.commit()

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al marcar código como usado: {str(e)}")