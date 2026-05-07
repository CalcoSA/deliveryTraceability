from app.domain.dtos.DeliveryRecordDto import (DeliveryRecordCreateDto, DeliveryRecordUpdateDto, DeliveryRecordBulkItemCreateDto)
from app.domain.entities.DeliveryRecord import DeliveryRecord
from app.domain.entities.Parameter import Parameter
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

class IDeliveryRecordRepository(ABC):

    @abstractmethod
    def getAll(self, deliveryDate: Optional[date] = None, IdPointSale: Optional[int] = None, IdDomiciliary: Optional[int] = None) -> List[DeliveryRecord]:
        pass

    @abstractmethod
    def getById(self, IdDeliveryRecord: int) -> Optional[DeliveryRecord]:
        pass

    @abstractmethod
    def getDuplicate(self, deliveryDate: date, IdPointSale: int, IdDomiciliary: int, excludeIdDeliveryRecord: Optional[int] = None) -> Optional[DeliveryRecord]:
        pass

    @abstractmethod
    def create(self, deliveryData: DeliveryRecordCreateDto, userId: int, parameter: Optional[Parameter]) -> DeliveryRecord:
        pass

    @abstractmethod
    def createMany(self, deliveryDate: date, IdPointSale: int, records: List[DeliveryRecordBulkItemCreateDto], userId: int, parameter: Optional[Parameter]) -> List[DeliveryRecord]:
        pass

    @abstractmethod
    def update(self, IdDeliveryRecord: int, deliveryData: DeliveryRecordUpdateDto, userId: int, parameter: Optional[Parameter]) -> Optional[DeliveryRecord]:
        pass

    @abstractmethod
    def delete(self, IdDeliveryRecord: int) -> bool:
        pass