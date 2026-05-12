from pydantic import BaseModel, ConfigDict

class AbsenceTypeResponseDto(BaseModel):
    IdAbsenceType: int
    nameAbsenceType: str
    statusAbsenceType: bool

    model_config = ConfigDict(from_attributes=True)