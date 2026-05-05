from app.domain.dtos.MenuOptionDto import MenuOptionResponseDto
from app.domain.dtos.RoleDto import RoleResponseDto
from pydantic import BaseModel
from typing import List

class LoginDto(BaseModel):
    username: str
    password: str

class AuthUserDto(BaseModel):
    IdApplicationUser: int
    wordpressUserId: int
    wordpressUserLogin: str
    wordpressUserEmail: str
    wordpressDisplayName: str
    roles: List[RoleResponseDto]
    menuOptions: List[MenuOptionResponseDto]

class AuthResponseDto(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    user: AuthUserDto

class IntranetAccessDto(BaseModel):
    userLogin: str
    ts: int
    sig: str