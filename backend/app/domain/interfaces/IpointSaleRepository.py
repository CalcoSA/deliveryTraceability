from app.domain.dtos.pointSaleDto import pointSaleCreateDto, pointSaleUpdateDto
from app.domain.entities.pointSale import pointSale
from abc import ABC, abstractmethod
from typing import List, Optional

class IpointSaleRepository(ABC):

    @abstractmethod
    def getAll(self) -> List[pointSale]:
        pass

    @abstractmethod
    def getById(self, IdPointSale: int) -> Optional[pointSale]:
        pass

    @abstractmethod
    def getByCodeInsensitive(self, codePointSale: str) -> Optional[pointSale]:
        pass

    @abstractmethod
    def create(self, pointSaleData: pointSaleCreateDto) -> pointSale:
        pass

    @abstractmethod
    def update(self, IdPointSale: int, pointSaleData: pointSaleUpdateDto) -> Optional[pointSale]:
        pass

    @abstractmethod
    def delete(self, IdPointSale: int) -> bool:
        pass