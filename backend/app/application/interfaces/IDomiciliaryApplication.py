from app.domain.dtos.DomiciliaryDto import DomiciliaryCreateDto, DomiciliaryUpdateDto
from app.domain.entities.Domiciliary import Domiciliary
from abc import ABC, abstractmethod
from typing import List, Optional

class IDomiciliaryApplication(ABC):

    @abstractmethod
    def getAll(self, pointSale: Optional[int] = None, statusDomiciliary: Optional[bool] = None) -> List[Domiciliary]:
        pass

    @abstractmethod
    def getById(self, IdDomiciliary: int) -> Domiciliary:
        pass

    @abstractmethod
    def getByDocument(self, documentDomiciliary: str) -> Domiciliary:
        pass

    @abstractmethod
    def getByPointSale(self, IdPointSale: int) -> List[Domiciliary]:
        pass

    @abstractmethod
    def create(self, domiciliaryData: DomiciliaryCreateDto) -> Domiciliary:
        pass

    @abstractmethod
    def update(self, IdDomiciliary: int, domiciliaryData: DomiciliaryUpdateDto) -> Domiciliary:
        pass

    @abstractmethod
    def delete(self, IdDomiciliary: int) -> bool:
        pass