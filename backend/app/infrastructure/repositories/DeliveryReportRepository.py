from app.domain.interfaces.IDeliveryReportRepository import IDeliveryReportRepository
from app.domain.dtos.DeliveryRecordDto import UpdateDeliveryQuantityResponseDto
from app.domain.entities.DeliverySettlement import DeliverySettlement
from app.domain.entities.ApplicationUser import ApplicationUser
from app.domain.entities.DeliveryRecord import DeliveryRecord
from app.domain.entities.AbsenceType import AbsenceType
from app.domain.entities.Domiciliary import Domiciliary
from app.domain.entities.pointSale import pointSale
from sqlalchemy.orm import Session, aliased
from typing import List, Optional
from sqlalchemy import func, case
from decimal import Decimal
from datetime import date

class DeliveryReportRepository(IDeliveryReportRepository):

    def __init__(self, db: Session):
        self.db = db

    def getSettlementReport(self, startDate: date, endDate: date, period: str, IdPointSale: Optional[int] = None, IdDomiciliary: Optional[int] = None) -> List[dict]:
        periodExpression = self._getPeriodExpression(period)
        CreatedUser = aliased(ApplicationUser)
        parameterNameExpression = func.coalesce(DeliverySettlement.parameterNameSettlement, "Costo")
        parameterValueExpression = func.coalesce(DeliverySettlement.parameterValueSettlement, 0)
        totalDeliveryQuantityExpression = func.sum(func.coalesce(DeliverySettlement.deliveryQuantitySettlement, 0))
        totalValueSettlementExpression = func.sum(func.coalesce(DeliverySettlement.totalValueSettlement, 0))
        totalAbsencesExpression = func.sum(case((DeliveryRecord.IdAbsenceType.isnot(None), 1), else_=0))
        absenceTypesExpression = func.group_concat(AbsenceType.nameAbsenceType)
        query = (
            self.db.query(
                DeliveryRecord.IdDeliveryRecord.label("IdDeliveryRecord"),
                periodExpression.label("periodKey"),
                pointSale.IdPointSale.label("IdPointSale"),
                pointSale.codePointSale.label("codePointSale"),
                pointSale.namePointSale.label("namePointSale"),
                Domiciliary.IdDomiciliary.label("IdDomiciliary"),
                Domiciliary.documentDomiciliary.label("documentDomiciliary"),
                Domiciliary.nameDomiciliary.label("nameDomiciliary"),
                parameterNameExpression.label("parameterNameSettlement"),
                parameterValueExpression.label("parameterValueSettlement"),
                totalDeliveryQuantityExpression.label("totalDeliveryQuantity"),
                totalAbsencesExpression.label("totalAbsences"),
                absenceTypesExpression.label("absenceTypes"),
                totalValueSettlementExpression.label("totalValueSettlement"),
                func.count(DeliveryRecord.IdDeliveryRecord).label("totalRecords"),
                func.group_concat(func.distinct(DeliveryRecord.createdByDeliveryRecord)).label("createdByUsers"))
            .select_from(DeliveryRecord)
            .outerjoin(
                DeliverySettlement,
                DeliverySettlement.IdDeliveryRecord == DeliveryRecord.IdDeliveryRecord
            )
            .outerjoin(
                AbsenceType,
                AbsenceType.IdAbsenceType == DeliveryRecord.IdAbsenceType
            )
            .join(
                pointSale,
                pointSale.IdPointSale == DeliveryRecord.IdPointSale
            )
            .join(
                Domiciliary,
                Domiciliary.IdDomiciliary == DeliveryRecord.IdDomiciliary
            )
            .outerjoin(
                CreatedUser,
                CreatedUser.wordpressUserId == DeliveryRecord.createdByDeliveryRecord
            )
            .filter(DeliveryRecord.deliveryDate >= startDate)
            .filter(DeliveryRecord.deliveryDate <= endDate)
        )

        if IdPointSale is not None:
            query = query.filter(DeliveryRecord.IdPointSale == IdPointSale)

        if IdDomiciliary is not None:
            query = query.filter(DeliveryRecord.IdDomiciliary == IdDomiciliary)

        rows = (
            query
            .group_by(
                DeliveryRecord.IdDeliveryRecord,
                periodExpression,
                pointSale.IdPointSale,
                pointSale.codePointSale,
                pointSale.namePointSale,
                Domiciliary.IdDomiciliary,
                Domiciliary.documentDomiciliary,
                Domiciliary.nameDomiciliary,
                parameterNameExpression,
                parameterValueExpression
            )
            .order_by(
                pointSale.namePointSale.asc(),
                pointSale.codePointSale.asc(),
                periodExpression.asc(),
                Domiciliary.nameDomiciliary.asc()
            )
            .all()
        )

        return [
            {
                "IdDeliveryRecord": row.IdDeliveryRecord,
                "periodType": period,
                "periodKey": str(row.periodKey),
                "periodLabel": self._getPeriodLabel(period, row.periodKey),
                "IdPointSale": row.IdPointSale,
                "codePointSale": row.codePointSale,
                "namePointSale": row.namePointSale,
                "IdDomiciliary": row.IdDomiciliary,
                "documentDomiciliary": row.documentDomiciliary,
                "nameDomiciliary": row.nameDomiciliary,
                "parameterNameSettlement": row.parameterNameSettlement,
                "parameterValueSettlement": row.parameterValueSettlement or Decimal("0"),
                "totalDeliveryQuantity": int(row.totalDeliveryQuantity or 0),
                "totalAbsences": int(row.totalAbsences or 0),
                "absenceTypes": row.absenceTypes or "",
                "totalValueSettlement": row.totalValueSettlement or Decimal("0"),
                "totalRecords": int(row.totalRecords or 0),
                "createdByUsers": row.createdByUsers,
            }
            for row in rows
        ]

    def _getPeriodExpression(self, period: str):
        if period == "day":
            return func.date_format(DeliveryRecord.deliveryDate, "%Y-%m-%d")

        if period == "week":
            return func.yearweek(DeliveryRecord.deliveryDate, 3)

        if period == "month":
            return func.date_format(DeliveryRecord.deliveryDate, "%Y-%m")

        return func.date_format(DeliveryRecord.deliveryDate, "%Y-%m-%d")

    def _getPeriodLabel(self, period: str, periodKey) -> str:
        if period == "day":
            return str(periodKey)

        if period == "week":
            return f"Semana {periodKey}"

        if period == "month":
            return str(periodKey)

        return str(periodKey)
    
    def updateDeliveryQuantityFromReport(self, IdDeliveryRecord: int, deliveryQuantity: int) -> UpdateDeliveryQuantityResponseDto:
        deliveryRecord = (self.db.query(DeliveryRecord).filter(DeliveryRecord.IdDeliveryRecord == IdDeliveryRecord).first())

        if deliveryRecord is None:
            raise ValueError("No existe el registro de domicilio que se desea editar.")

        deliverySettlement = (self.db.query(DeliverySettlement).filter(DeliverySettlement.IdDeliveryRecord == IdDeliveryRecord).first())

        if deliverySettlement is None:
            raise ValueError("No existe liquidación asociada al registro de domicilio.")

        deliveryRecord.deliveryQuantity = deliveryQuantity
        deliverySettlement.deliveryQuantitySettlement = deliveryQuantity
        deliverySettlement.totalValueSettlement = ( deliverySettlement.parameterValueSettlement * deliveryQuantity)

        self.db.commit()
        self.db.refresh(deliveryRecord)
        self.db.refresh(deliverySettlement)

        return UpdateDeliveryQuantityResponseDto(
            IdDeliveryRecord=deliveryRecord.IdDeliveryRecord,
            deliveryDate=deliveryRecord.deliveryDate,
            IdPointSale=deliveryRecord.IdPointSale,
            IdDomiciliary=deliveryRecord.IdDomiciliary,
            deliveryQuantity=deliveryRecord.deliveryQuantity,
            IdDeliverySettlement=deliverySettlement.IdDeliverySettlement,
            IdParameter=deliverySettlement.IdParameter,
            parameterNameSettlement=deliverySettlement.parameterNameSettlement,
            parameterValueSettlement=deliverySettlement.parameterValueSettlement,
            deliveryQuantitySettlement=deliverySettlement.deliveryQuantitySettlement,
            totalValueSettlement=deliverySettlement.totalValueSettlement
        )