from app.domain.entities.PointSaleEmail import PointSaleEmail
from abc import ABC, abstractmethod
from typing import List, Optional

class IPointSaleEmailRepository(ABC):

    @abstractmethod
    def getAll(self) -> List[PointSaleEmail]:
        pass

    @abstractmethod
    def getById(self, IdPointSaleEmail: int) -> Optional[PointSaleEmail]:
        pass

    @abstractmethod
    def getByEmail(self, emailPointSale: str) -> Optional[PointSaleEmail]:
        pass

    @abstractmethod
    def create(self, emailPointSale: str) -> PointSaleEmail:
        pass

    @abstractmethod
    def update(self, IdPointSaleEmail: int, emailPointSale: Optional[str], statusPointSaleEmail: Optional[bool]) -> Optional[PointSaleEmail]:
        pass

    @abstractmethod
    def delete(self, IdPointSaleEmail: int) -> bool:
        pass