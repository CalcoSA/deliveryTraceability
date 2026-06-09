from app.domain.dtos.PointSaleEmailDto import PointSaleEmailCreateDto, PointSaleEmailUpdateDto
from app.domain.entities.PointSaleEmail import PointSaleEmail
from abc import ABC, abstractmethod
from typing import List

class IPointSaleEmailApplication(ABC):

    @abstractmethod
    def getAll(self) -> List[PointSaleEmail]:
        pass

    @abstractmethod
    def getById(self, IdPointSaleEmail: int) -> PointSaleEmail:
        pass

    @abstractmethod
    def create(self, data: PointSaleEmailCreateDto) -> PointSaleEmail:
        pass

    @abstractmethod
    def update(self, IdPointSaleEmail: int, data: PointSaleEmailUpdateDto) -> PointSaleEmail:
        pass

    @abstractmethod
    def delete(self, IdPointSaleEmail: int) -> bool:
        pass