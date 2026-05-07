from app.domain.dtos.DeliveryRecordDto import DeliveryRecordCreateDto, DeliveryRecordUpdateDto, DeliveryRecordBulkCreateDto
from app.domain.entities.DeliveryRecord import DeliveryRecord
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

class IDeliveryRecordApplication(ABC):

    @abstractmethod
    def getAll(self, deliveryDate: Optional[date] = None, IdPointSale: Optional[int] = None, IdDomiciliary: Optional[int] = None) -> List[DeliveryRecord]:
        pass

    @abstractmethod
    def getById(self, IdDeliveryRecord: int) -> DeliveryRecord:
        pass

    @abstractmethod
    def create(self, deliveryData: DeliveryRecordCreateDto, userId: int) -> DeliveryRecord:
        pass

    @abstractmethod
    def createMany(self, deliveryData: DeliveryRecordBulkCreateDto, userId: int) -> List[DeliveryRecord]:
        pass

    @abstractmethod
    def update(self, IdDeliveryRecord: int, deliveryData: DeliveryRecordUpdateDto, userId: int) -> DeliveryRecord:
        pass

    @abstractmethod
    def delete(self, IdDeliveryRecord: int) -> bool:
        pass