from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ParameterCreateDto(BaseModel):
    nameParameter: str
    valueParameter: str

class ParameterUpdateDto(BaseModel):
    nameParameter: Optional[str] = None
    valueParameter: Optional[str] = None

class ParameterResponseDto(BaseModel):
    IdParameter: int
    nameParameter: str
    valueParameter: str
    createdByParameter: str
    createdAtParameter: datetime
    updatedByParameter: Optional[str] = None
    updatedAtParameter: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)