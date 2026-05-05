from app.infrastructure.repositories.ApplicationUserRepository import ApplicationUserRepository
from app.infrastructure.repositories.WordpressUserRepository import WordpressUserRepository
from app.application.services.WordpressPasswordVerifier import WordpressPasswordVerifier
from app.application.interfaces.IAuthApplication import IAuthApplication
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.application.services.AuthApplication import AuthApplication
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.infrastructure.db.wordpressConnection import getWordpressDb
from app.domain.dtos.AuthDto import LoginDto, AuthResponseDto
from app.application.services.JwtService import JwtService
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
import jwt

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

def getAuthApplication(db: Session = Depends(getDb), wpDb: Session = Depends(getWordpressDb)) -> IAuthApplication:
    applicationUserRepository = ApplicationUserRepository(db)
    wordpressUserRepository = WordpressUserRepository(wpDb)
    wordpressPasswordVerifier = WordpressPasswordVerifier()
    return AuthApplication(applicationUserRepository, wordpressUserRepository, wordpressPasswordVerifier)


def getCurrentPayload(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        return JwtService.decodeToken(credentials.credentials)
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="La sesión expiró.")
    
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")

@router.post("/login", response_model=apiResponseDto[AuthResponseDto])
def login(loginData: LoginDto, service: IAuthApplication = Depends(getAuthApplication)):
    try:
        data = service.login(loginData)
        return apiResponseDto(isSuccess=True, Message="Inicio de sesión correcto.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al iniciar sesión.")


@router.get("/intranet-access", response_model=apiResponseDto[AuthResponseDto])
def intranetAccess(userLogin: str = Query(...), ts: int = Query(...), sig: str = Query(...), service: IAuthApplication = Depends(getAuthApplication)):
    try:
        data = service.intranetAccess(userLogin, ts, sig)
        return apiResponseDto(isSuccess=True, Message="Acceso desde intranet correcto.", result=data)

    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al validar el acceso desde intranet.")

@router.get("/me", response_model=apiResponseDto[AuthResponseDto])
def me(payload: dict = Depends(getCurrentPayload), service: IAuthApplication = Depends(getAuthApplication)):
    try:
        data = service.getCurrentUser(payload["wordpressUserId"])
        return apiResponseDto(isSuccess=True, Message="Usuario autenticado obtenido correctamente.", result=data)

    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el usuario autenticado.")