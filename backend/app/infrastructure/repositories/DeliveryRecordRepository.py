from app.domain.dtos.DeliveryRecordDto import DeliveryRecordCreateDto, DeliveryRecordUpdateDto, DeliveryRecordBulkItemCreateDto
from app.domain.interfaces.IDeliveryRecordRepository import IDeliveryRecordRepository
from app.domain.entities.DeliverySettlement import DeliverySettlement
from app.domain.entities.DeliveryRecord import DeliveryRecord
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import date, datetime, timedelta, timezone
from app.domain.entities.Parameter import Parameter
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from decimal import Decimal

class DeliveryRecordRepository(IDeliveryRecordRepository):

    def __init__(self, db: Session):
        self.db = db

    def _nowBogota(self) -> datetime:
        colombiaTimezone = timezone(timedelta(hours=-5))
        return datetime.now(colombiaTimezone).replace(tzinfo=None)
    
    def _fieldWasSent(self, dto, fieldName: str) -> bool:
        fieldsSet = getattr(dto, "model_fields_set", None)

        if fieldsSet is None:
            fieldsSet = getattr(dto, "__fields_set__", set())

        return fieldName in fieldsSet

    def getAll(self, deliveryDate: Optional[date] = None, IdPointSale: Optional[int] = None, IdDomiciliary: Optional[int] = None) -> List[DeliveryRecord]:
        query = (self.db.query(DeliveryRecord).options(joinedload(DeliveryRecord.settlement)).options(joinedload(DeliveryRecord.absenceTypeRelation)))

        if deliveryDate is not None:
            query = query.filter(DeliveryRecord.deliveryDate == deliveryDate)

        if IdPointSale is not None:
            query = query.filter(DeliveryRecord.IdPointSale == IdPointSale)

        if IdDomiciliary is not None:
            query = query.filter(DeliveryRecord.IdDomiciliary == IdDomiciliary)

        return (query.order_by(DeliveryRecord.deliveryDate.desc(), DeliveryRecord.IdDeliveryRecord.desc()).all())

    def getById(self, IdDeliveryRecord: int) -> Optional[DeliveryRecord]:
        return (self.db.query(DeliveryRecord).options(joinedload(DeliveryRecord.settlement)).options(joinedload(DeliveryRecord.absenceTypeRelation)).filter(DeliveryRecord.IdDeliveryRecord == IdDeliveryRecord).first())

    def getDuplicate(self, deliveryDate: date, IdPointSale: int, IdDomiciliary: int, excludeIdDeliveryRecord: Optional[int] = None) -> Optional[DeliveryRecord]:
        query = (self.db.query(DeliveryRecord).filter(DeliveryRecord.deliveryDate == deliveryDate).filter(DeliveryRecord.IdPointSale == IdPointSale).filter(DeliveryRecord.IdDomiciliary == IdDomiciliary))

        if excludeIdDeliveryRecord is not None:
            query = query.filter(DeliveryRecord.IdDeliveryRecord != excludeIdDeliveryRecord)

        return query.first()

    def create(self, deliveryData: DeliveryRecordCreateDto, userId: int, parameter: Optional[Parameter]) -> DeliveryRecord:
        try:
            now = self._nowBogota()
            hasAbsence = deliveryData.IdAbsenceType is not None
            deliveryQuantity = 0 if hasAbsence else int(deliveryData.deliveryQuantity)

            newDeliveryRecord = DeliveryRecord(
                deliveryDate=deliveryData.deliveryDate,
                IdPointSale=deliveryData.IdPointSale,
                IdDomiciliary=deliveryData.IdDomiciliary,
                deliveryQuantity=deliveryQuantity,
                IdAbsenceType=deliveryData.IdAbsenceType,
                createdByDeliveryRecord=userId,
                createdAtDeliveryRecord=now,
                updatedByDeliveryRecord=None,
                updatedAtDeliveryRecord=None
            )

            self.db.add(newDeliveryRecord)
            self.db.flush()

            if not hasAbsence and parameter is not None:
                parameterValue = Decimal(str(parameter.valueParameter))
                totalValue = parameterValue * Decimal(deliveryQuantity)

                newSettlement = DeliverySettlement(
                    IdDeliveryRecord=newDeliveryRecord.IdDeliveryRecord,
                    IdParameter=parameter.IdParameter,
                    parameterNameSettlement=parameter.nameParameter,
                    parameterValueSettlement=parameterValue,
                    deliveryQuantitySettlement=deliveryQuantity,
                    totalValueSettlement=totalValue,
                    createdBySettlement=userId,
                    createdAtSettlement=now,
                    updatedBySettlement=None,
                    updatedAtSettlement=None
                )

                self.db.add(newSettlement)

            self.db.commit()
            self.db.refresh(newDeliveryRecord)

            return self.getById(newDeliveryRecord.IdDeliveryRecord)

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un registro para esa fecha, punto de venta y domiciliario.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear el registro de domicilio: {str(e)}")
        
    def createMany(self, deliveryDate: date, IdPointSale: int, records: List[DeliveryRecordBulkItemCreateDto], userId: int, parameter: Optional[Parameter]) -> List[DeliveryRecord]:
        try:
            now = self._nowBogota()
            createdIds = []

            for item in records:
                hasAbsence = item.IdAbsenceType is not None
                deliveryQuantity = 0 if hasAbsence else int(item.deliveryQuantity)

                newDeliveryRecord = DeliveryRecord(
                    deliveryDate=deliveryDate,
                    IdPointSale=IdPointSale,
                    IdDomiciliary=item.IdDomiciliary,
                    deliveryQuantity=deliveryQuantity,
                    IdAbsenceType=item.IdAbsenceType,
                    createdByDeliveryRecord=userId,
                    createdAtDeliveryRecord=now,
                    updatedByDeliveryRecord=None,
                    updatedAtDeliveryRecord=None
                )

                self.db.add(newDeliveryRecord)
                self.db.flush()

                createdIds.append(newDeliveryRecord.IdDeliveryRecord)

                if not hasAbsence and parameter is not None:
                    parameterValue = Decimal(str(parameter.valueParameter))
                    totalValue = parameterValue * Decimal(deliveryQuantity)

                    newSettlement = DeliverySettlement(
                        IdDeliveryRecord=newDeliveryRecord.IdDeliveryRecord,
                        IdParameter=parameter.IdParameter,
                        parameterNameSettlement=parameter.nameParameter,
                        parameterValueSettlement=parameterValue,
                        deliveryQuantitySettlement=deliveryQuantity,
                        totalValueSettlement=totalValue,
                        createdBySettlement=userId,
                        createdAtSettlement=now,
                        updatedBySettlement=None,
                        updatedAtSettlement=None
                    )

                    self.db.add(newSettlement)

            self.db.commit()

            return [self.getById(IdDeliveryRecord) for IdDeliveryRecord in createdIds]

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Uno o varios registros ya existen para esa fecha, punto de venta y domiciliario.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear los registros de domicilio: {str(e)}")

    def update(self, IdDeliveryRecord: int, deliveryData: DeliveryRecordUpdateDto, userId: int, parameter: Optional[Parameter]) -> Optional[DeliveryRecord]:

        try:
            deliveryRecordFound = self.getById(IdDeliveryRecord)

            if not deliveryRecordFound:
                return None

            now = self._nowBogota()

            if deliveryData.deliveryDate is not None:
                deliveryRecordFound.deliveryDate = deliveryData.deliveryDate

            if deliveryData.IdPointSale is not None:
                deliveryRecordFound.IdPointSale = deliveryData.IdPointSale

            if deliveryData.IdDomiciliary is not None:
                deliveryRecordFound.IdDomiciliary = deliveryData.IdDomiciliary

            if self._fieldWasSent(deliveryData, "IdAbsenceType"):
                deliveryRecordFound.IdAbsenceType = deliveryData.IdAbsenceType

            hasAbsence = deliveryRecordFound.IdAbsenceType is not None

            if hasAbsence:
                deliveryRecordFound.deliveryQuantity = 0

                if deliveryRecordFound.settlement:
                    self.db.delete(deliveryRecordFound.settlement)

            else:
                if deliveryData.deliveryQuantity is not None:
                    deliveryRecordFound.deliveryQuantity = deliveryData.deliveryQuantity

                quantity = int(deliveryRecordFound.deliveryQuantity)

                if parameter is not None:
                    parameterValue = Decimal(str(parameter.valueParameter))
                    totalValue = parameterValue * Decimal(quantity)

                    if deliveryRecordFound.settlement:
                        deliveryRecordFound.settlement.IdParameter = parameter.IdParameter
                        deliveryRecordFound.settlement.parameterNameSettlement = parameter.nameParameter
                        deliveryRecordFound.settlement.parameterValueSettlement = parameterValue
                        deliveryRecordFound.settlement.deliveryQuantitySettlement = quantity
                        deliveryRecordFound.settlement.totalValueSettlement = totalValue
                        deliveryRecordFound.settlement.updatedBySettlement = userId
                        deliveryRecordFound.settlement.updatedAtSettlement = now
                    else:
                        newSettlement = DeliverySettlement(
                            IdDeliveryRecord=deliveryRecordFound.IdDeliveryRecord,
                            IdParameter=parameter.IdParameter,
                            parameterNameSettlement=parameter.nameParameter,
                            parameterValueSettlement=parameterValue,
                            deliveryQuantitySettlement=quantity,
                            totalValueSettlement=totalValue,
                            createdBySettlement=userId,
                            createdAtSettlement=now,
                            updatedBySettlement=None,
                            updatedAtSettlement=None
                        )

                        self.db.add(newSettlement)

            deliveryRecordFound.updatedByDeliveryRecord = userId
            deliveryRecordFound.updatedAtDeliveryRecord = now

            self.db.commit()
            self.db.refresh(deliveryRecordFound)

            return self.getById(IdDeliveryRecord)

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un registro para esa fecha, punto de venta y domiciliario.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar el registro de domicilio: {str(e)}")

    def delete(self, IdDeliveryRecord: int) -> bool:
        try:
            deliveryRecordFound = self.getById(IdDeliveryRecord)

            if not deliveryRecordFound:
                return False

            self.db.delete(deliveryRecordFound)
            self.db.commit()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar el registro de domicilio: {str(e)}")