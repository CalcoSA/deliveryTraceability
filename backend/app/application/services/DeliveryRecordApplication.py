from app.domain.dtos.DeliveryRecordDto import DeliveryRecordCreateDto, DeliveryRecordUpdateDto, DeliveryRecordBulkCreateDto
from app.application.interfaces.IDeliveryRecordApplication import IDeliveryRecordApplication
from app.domain.interfaces.IDeliveryRecordRepository import IDeliveryRecordRepository
from app.domain.interfaces.IDomiciliaryRepository import IDomiciliaryRepository
from app.domain.interfaces.IParameterRepository import IParameterRepository
from app.domain.interfaces.IpointSaleRepository import IpointSaleRepository
from app.domain.entities.DeliveryRecord import DeliveryRecord
from app.domain.entities.Parameter import Parameter
from decimal import Decimal, InvalidOperation
from typing import List, Optional
from datetime import date

DELIVERY_VALUE_PARAMETER_NAME = "Costo"

class DeliveryRecordApplication(IDeliveryRecordApplication):

    def __init__(self, deliveryRecordRepository: IDeliveryRecordRepository, pointSaleRepository: IpointSaleRepository, domiciliaryRepository: IDomiciliaryRepository, parameterRepository: IParameterRepository):
        self.deliveryRecordRepository = deliveryRecordRepository
        self.pointSaleRepository = pointSaleRepository
        self.domiciliaryRepository = domiciliaryRepository
        self.parameterRepository = parameterRepository

    def getAll(self, deliveryDate: Optional[date] = None, IdPointSale: Optional[int] = None,IdDomiciliary: Optional[int] = None) -> List[DeliveryRecord]:
        return self.deliveryRecordRepository.getAll(deliveryDate, IdPointSale, IdDomiciliary)

    def getById(self, IdDeliveryRecord: int) -> DeliveryRecord:
        deliveryRecordFound = self.deliveryRecordRepository.getById(IdDeliveryRecord)

        if not deliveryRecordFound:
            raise ValueError("Registro de domicilio no encontrado.")

        return deliveryRecordFound

    def create(self, deliveryData: DeliveryRecordCreateDto, userId: int) -> DeliveryRecord:
        self._validateBaseData(deliveryData.IdPointSale, deliveryData.IdDomiciliary)
        self._validateDeliveryQuantity(deliveryData.isRestDay, deliveryData.deliveryQuantity)

        duplicate = self.deliveryRecordRepository.getDuplicate(deliveryData.deliveryDate, deliveryData.IdPointSale, deliveryData.IdDomiciliary)

        if duplicate:
            raise ValueError("Ya existe un registro para esa fecha, punto de venta y domiciliario.")

        parameter = None

        if not deliveryData.isRestDay:
            parameter = self._getAndValidateDeliveryValueParameter()

        return self.deliveryRecordRepository.create(deliveryData, userId, parameter)
    
    def createMany(self, deliveryData: DeliveryRecordBulkCreateDto, userId: int) -> List[DeliveryRecord]:

        if not deliveryData.records:
            raise ValueError("Debes enviar al menos un domiciliario.")

        pointSaleFound = self.pointSaleRepository.getById(deliveryData.IdPointSale)

        if not pointSaleFound:
            raise ValueError("El punto de venta no existe.")

        domiciliaryIds = [item.IdDomiciliary for item in deliveryData.records]

        if len(domiciliaryIds) != len(set(domiciliaryIds)):
            raise ValueError("No puedes enviar domiciliarios repetidos.")

        hasNormalDelivery = False

        for item in deliveryData.records:
            domiciliaryFound = self.domiciliaryRepository.getById(item.IdDomiciliary)

            if not domiciliaryFound:
                raise ValueError(f"El domiciliario {item.IdDomiciliary} no existe.")

            if domiciliaryFound.pointSale != deliveryData.IdPointSale:
                raise ValueError(f"El domiciliario {domiciliaryFound.nameDomiciliary} no pertenece al punto de venta enviado.")

            self._validateDeliveryQuantity(item.isRestDay, item.deliveryQuantity)

            if not item.isRestDay:
                hasNormalDelivery = True

            duplicate = self.deliveryRecordRepository.getDuplicate(deliveryData.deliveryDate, deliveryData.IdPointSale, item.IdDomiciliary)

            if duplicate:
                raise ValueError(f"Ya existe un registro para el domiciliario {domiciliaryFound.nameDomiciliary} en esa fecha.")

        parameter = None

        if hasNormalDelivery:
            parameter = self._getAndValidateDeliveryValueParameter()

        return self.deliveryRecordRepository.createMany(deliveryData.deliveryDate, deliveryData.IdPointSale, deliveryData.records, userId, parameter)

    def update(self, IdDeliveryRecord: int, deliveryData: DeliveryRecordUpdateDto, userId: int) -> DeliveryRecord:
        deliveryRecordFound = self.deliveryRecordRepository.getById(IdDeliveryRecord)

        if not deliveryRecordFound:
            raise ValueError("Registro de domicilio no encontrado.")

        finalDeliveryDate = deliveryData.deliveryDate or deliveryRecordFound.deliveryDate
        finalIdPointSale = deliveryData.IdPointSale or deliveryRecordFound.IdPointSale
        finalIdDomiciliary = deliveryData.IdDomiciliary or deliveryRecordFound.IdDomiciliary

        finalIsRestDay = (
            deliveryData.isRestDay
            if deliveryData.isRestDay is not None
            else deliveryRecordFound.isRestDay
        )

        finalDeliveryQuantity = (
            deliveryData.deliveryQuantity
            if deliveryData.deliveryQuantity is not None
            else deliveryRecordFound.deliveryQuantity
        )

        self._validateBaseData(finalIdPointSale, finalIdDomiciliary)
        self._validateDeliveryQuantity(finalIsRestDay, finalDeliveryQuantity)

        duplicate = self.deliveryRecordRepository.getDuplicate(finalDeliveryDate, finalIdPointSale, finalIdDomiciliary, IdDeliveryRecord)

        if duplicate:
            raise ValueError("Ya existe un registro para esa fecha, punto de venta y domiciliario.")

        parameter = None

        if not finalIsRestDay:
            parameter = self._getAndValidateDeliveryValueParameter()

        deliveryUpdated = self.deliveryRecordRepository.update(IdDeliveryRecord, deliveryData, userId, parameter)

        if not deliveryUpdated:
            raise ValueError("Registro de domicilio no encontrado.")

        return deliveryUpdated

    def delete(self, IdDeliveryRecord: int) -> bool:
        deliveryRecordFound = self.deliveryRecordRepository.getById(IdDeliveryRecord)

        if not deliveryRecordFound:
            raise ValueError("Registro de domicilio no encontrado.")

        return self.deliveryRecordRepository.delete(IdDeliveryRecord)

    def _validateBaseData(self, IdPointSale: int, IdDomiciliary: int) -> None:
        pointSaleFound = self.pointSaleRepository.getById(IdPointSale)

        if not pointSaleFound:
            raise ValueError("El punto de venta no existe.")

        domiciliaryFound = self.domiciliaryRepository.getById(IdDomiciliary)

        if not domiciliaryFound:
            raise ValueError("El domiciliario no existe.")

        if domiciliaryFound.pointSale != IdPointSale:
            raise ValueError("El domiciliario no pertenece al punto de venta enviado.")

    def _validateDeliveryQuantity(self, isRestDay: bool, deliveryQuantity: Optional[int]) -> None:
        if isRestDay:
            return

        if deliveryQuantity is None:
            raise ValueError("El número de domicilios es obligatorio cuando no es descanso.")

        if deliveryQuantity <= 0:
            raise ValueError("El número de domicilios debe ser mayor a cero.")

    def _getAndValidateDeliveryValueParameter(self) -> Parameter:
        parameter = self.parameterRepository.getByName(DELIVERY_VALUE_PARAMETER_NAME)

        if not parameter:
            raise ValueError(f"No existe el parámetro {DELIVERY_VALUE_PARAMETER_NAME}.")

        try:
            value = Decimal(str(parameter.valueParameter))
        except InvalidOperation:
            raise ValueError(f"El parámetro {DELIVERY_VALUE_PARAMETER_NAME} debe tener un valor numérico.")

        if value <= 0:
            raise ValueError(f"El parámetro {DELIVERY_VALUE_PARAMETER_NAME} debe ser mayor a cero.")

        return parameter