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

class ParameterHistoryResponseDto(BaseModel):
    IdParameterHistory: int
    IdParameter: int
    actionParameterHistory: str
    previousNameParameter: Optional[str] = None
    newNameParameter: Optional[str] = None
    previousValueParameter: Optional[str] = None
    newValueParameter: Optional[str] = None
    createdByParameterHistory: str
    createdAtParameterHistory: datetime

    model_config = ConfigDict(from_attributes=True)