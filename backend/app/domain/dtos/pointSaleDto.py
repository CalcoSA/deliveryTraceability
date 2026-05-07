from pydantic import BaseModel, ConfigDict
from typing import Optional

class pointSaleBaseDto(BaseModel):
    codePointSale: str
    namePointSale: str
    statusPointSale: bool

class pointSaleCreateDto(pointSaleBaseDto):
    pass

class pointSaleUpdateDto(BaseModel):
    codePointSale: Optional[str] = None
    namePointSale: Optional[str] = None
    statusPointSale: Optional[bool] = None

class pointSaleResponseDto(pointSaleBaseDto):
    IdPointSale: int

    model_config = ConfigDict(from_attributes=True)