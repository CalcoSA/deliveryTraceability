from typing import Generic, Optional, TypeVar
from pydantic.generics import GenericModel
from pydantic import BaseModel

T = TypeVar("T")

class apiResponseDto(GenericModel, Generic[T]):
    isSuccess: bool
    Message: str
    result: Optional[T] = None