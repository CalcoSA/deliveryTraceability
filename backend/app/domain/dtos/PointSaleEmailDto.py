from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional

class PointSaleEmailCreateDto(BaseModel):
    emailPointSale: EmailStr

class PointSaleEmailUpdateDto(BaseModel):
    emailPointSale: Optional[EmailStr] = None
    statusPointSaleEmail: Optional[bool] = None

class PointSaleEmailResponseDto(BaseModel):
    IdPointSaleEmail: int
    emailPointSale: str
    statusPointSaleEmail: bool
    createdAtPointSaleEmail: datetime
    updatedAtPointSaleEmail: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)