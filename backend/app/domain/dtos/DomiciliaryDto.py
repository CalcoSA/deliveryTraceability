from pydantic import BaseModel, ConfigDict
from typing import Optional

class DomiciliaryBaseDto(BaseModel):
    documentDomiciliary: str
    nameDomiciliary: str
    statusDomiciliary: bool
    pointSale: int

class DomiciliaryCreateDto(DomiciliaryBaseDto):
    pass

class DomiciliaryUpdateDto(BaseModel):
    documentDomiciliary: Optional[str] = None
    nameDomiciliary: Optional[str] = None
    statusDomiciliary: Optional[bool] = None
    pointSale: Optional[int] = None

class DomiciliaryResponseDto(DomiciliaryBaseDto):
    IdDomiciliary: int

    model_config = ConfigDict(from_attributes=True)