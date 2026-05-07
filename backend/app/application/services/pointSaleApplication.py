from app.application.interfaces.IpointSaleApplication import IpointSaleApplication
from app.domain.dtos.pointSaleDto import pointSaleCreateDto, pointSaleUpdateDto
from app.domain.interfaces.IpointSaleRepository import IpointSaleRepository
from app.domain.entities.pointSale import pointSale
from typing import List, Optional

class pointSaleApplication(IpointSaleApplication):
    def __init__(self, pointSaleRepository: IpointSaleRepository):
        self.pointSaleRepository = pointSaleRepository

    def getAll(self) -> List[pointSale]:
        return self.pointSaleRepository.getAll()

    def getById(self, IdPointSale: int) -> Optional[pointSale]:
        return self.pointSaleRepository.getById(IdPointSale)

    def create(self, pointSaleData: pointSaleCreateDto) -> pointSale:
        existingPointSale = self.pointSaleRepository.getByCodeInsensitive(pointSaleData.codePointSale)

        if existingPointSale:
            raise ValueError("Ya existe un Punto de Venta con ese código.")
        
        return self.pointSaleRepository.create(pointSaleData)

    def update(self, IdPointSale: int, pointSaleData: pointSaleUpdateDto) -> Optional[pointSale]:
        pointSaleFound = self.pointSaleRepository.getById(IdPointSale)

        if not pointSaleFound:
            return None

        if pointSaleData.codePointSale is not None:
            existingPointSale = self.pointSaleRepository.getByCodeInsensitive(pointSaleData.codePointSale)

            if existingPointSale and existingPointSale.IdPointSale != IdPointSale:
                raise ValueError("Ya existe un Punto de Venta con ese código.")

        return self.pointSaleRepository.update(IdPointSale, pointSaleData)

    def delete(self, IdPointSale: int) -> bool:
        return self.pointSaleRepository.delete(IdPointSale)