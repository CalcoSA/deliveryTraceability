from app.domain.dtos.PointSaleEmailDto import PointSaleEmailCreateDto, PointSaleEmailUpdateDto
from app.application.interfaces.IPointSaleEmailApplication import IPointSaleEmailApplication
from app.domain.interfaces.IPointSaleEmailRepository import IPointSaleEmailRepository
from app.domain.entities.PointSaleEmail import PointSaleEmail
from typing import List

class PointSaleEmailApplication(IPointSaleEmailApplication):

    def __init__(self, pointSaleEmailRepository: IPointSaleEmailRepository):
        self.pointSaleEmailRepository = pointSaleEmailRepository

    def getAll(self) -> List[PointSaleEmail]:
        return self.pointSaleEmailRepository.getAll()

    def getById(self, IdPointSaleEmail: int) -> PointSaleEmail:
        emailFound = self.pointSaleEmailRepository.getById(IdPointSaleEmail)

        if not emailFound:
            raise ValueError("Correo de punto de venta no encontrado.")

        return emailFound

    def create(self, data: PointSaleEmailCreateDto) -> PointSaleEmail:
        email = str(data.emailPointSale).strip().lower()

        if self.pointSaleEmailRepository.getByEmail(email):
            raise ValueError("Ya existe un correo de punto de venta registrado.")

        return self.pointSaleEmailRepository.create(email)

    def update(self, IdPointSaleEmail: int, data: PointSaleEmailUpdateDto) -> PointSaleEmail:
        emailFound = self.pointSaleEmailRepository.getById(IdPointSaleEmail)

        if not emailFound:
            raise ValueError("Correo de punto de venta no encontrado.")

        email = str(data.emailPointSale).strip().lower() if data.emailPointSale is not None else None

        if email is not None:
            emailExists = self.pointSaleEmailRepository.getByEmail(email)

            if emailExists and emailExists.IdPointSaleEmail != IdPointSaleEmail:
                raise ValueError("Ya existe un correo de punto de venta registrado.")

        updated = self.pointSaleEmailRepository.update(IdPointSaleEmail, email, data.statusPointSaleEmail)

        if not updated:
            raise ValueError("Correo de punto de venta no encontrado.")

        return updated

    def delete(self, IdPointSaleEmail: int) -> bool:
        emailFound = self.pointSaleEmailRepository.getById(IdPointSaleEmail)

        if not emailFound:
            raise ValueError("Correo de punto de venta no encontrado.")

        return self.pointSaleEmailRepository.delete(IdPointSaleEmail)