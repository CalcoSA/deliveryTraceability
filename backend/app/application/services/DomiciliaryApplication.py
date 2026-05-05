from app.application.interfaces.IDomiciliaryApplication import IDomiciliaryApplication
from app.domain.dtos.DomiciliaryDto import DomiciliaryCreateDto, DomiciliaryUpdateDto
from app.domain.interfaces.IDomiciliaryRepository import IDomiciliaryRepository
from app.domain.interfaces.IpointSaleRepository import IpointSaleRepository
from app.domain.entities.Domiciliary import Domiciliary
from typing import List

class DomiciliaryApplication(IDomiciliaryApplication):
    def __init__(self, domiciliaryRepository: IDomiciliaryRepository, pointSaleRepository: IpointSaleRepository):
        self.domiciliaryRepository = domiciliaryRepository
        self.pointSaleRepository = pointSaleRepository

    def getAll(self, pointSale: int | None = None, statusDomiciliary: bool | None = None) -> List[Domiciliary]:

        if pointSale is not None:
            pointSaleFound = self.pointSaleRepository.getById(pointSale)

            if not pointSaleFound:
                raise ValueError("El punto de venta no existe.")

        return self.domiciliaryRepository.getAll(pointSale, statusDomiciliary)

    def getById(self, IdDomiciliary: int) -> Domiciliary:
        domiciliaryFound = self.domiciliaryRepository.getById(IdDomiciliary)

        if not domiciliaryFound:
            raise ValueError("Domiciliario no encontrado.")

        return domiciliaryFound
    
    def getByDocument(self, documentDomiciliary: str) -> Domiciliary:
        domiciliaryFound = self.domiciliaryRepository.getByDocument(documentDomiciliary.strip())

        if not domiciliaryFound:
            raise ValueError("Domiciliario no encontrado.")

        return domiciliaryFound
    
    def getByPointSale(self, IdPointSale: int) -> List[Domiciliary]:
        pointSaleFound = self.pointSaleRepository.getById(IdPointSale)

        if not pointSaleFound:
            raise ValueError("El punto de venta no existe.")

        return self.domiciliaryRepository.getByPointSale(IdPointSale)

    def create(self, domiciliaryData: DomiciliaryCreateDto) -> Domiciliary:
        pointSaleFound = self.pointSaleRepository.getById(domiciliaryData.pointSale)

        if not pointSaleFound:
            raise ValueError("El punto de venta asociado no existe.")

        documentExists = self.domiciliaryRepository.getByDocument(domiciliaryData.documentDomiciliary)

        if documentExists:
            raise ValueError("Ya existe un domiciliario con ese documento.")

        return self.domiciliaryRepository.create(domiciliaryData)

    def update(self, IdDomiciliary: int, domiciliaryData: DomiciliaryUpdateDto) -> Domiciliary:
        domiciliaryFound = self.domiciliaryRepository.getById(IdDomiciliary)

        if not domiciliaryFound:
            raise ValueError("Domiciliario no encontrado.")

        if domiciliaryData.pointSale is not None:
            pointSaleFound = self.pointSaleRepository.getById(domiciliaryData.pointSale)

            if not pointSaleFound:
                raise ValueError("El punto de venta asociado no existe.")

        if domiciliaryData.documentDomiciliary is not None:
            documentExists = self.domiciliaryRepository.getByDocument(domiciliaryData.documentDomiciliary)

            if documentExists and documentExists.IdDomiciliary != IdDomiciliary:
                raise ValueError("Ya existe un domiciliario con ese documento.")

        domiciliaryUpdated = self.domiciliaryRepository.update(IdDomiciliary, domiciliaryData)

        if not domiciliaryUpdated:
            raise ValueError("Domiciliario no encontrado.")

        return domiciliaryUpdated

    def delete(self, IdDomiciliary: int) -> bool:
        domiciliaryFound = self.domiciliaryRepository.getById(IdDomiciliary)

        if not domiciliaryFound:
            raise ValueError("Domiciliario no encontrado.")

        return self.domiciliaryRepository.delete(IdDomiciliary)