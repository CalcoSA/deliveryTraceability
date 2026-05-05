from app.domain.dtos.ApplicationUserDto import ( ApplicationUserCreateDto, ApplicationUserUpdateDto, ApplicationUserResponseDto )
from app.infrastructure.repositories.ApplicationUserRepository import ApplicationUserRepository
from app.application.interfaces.IApplicationUserApplication import IApplicationUserApplication
from app.infrastructure.repositories.WordpressUserRepository import WordpressUserRepository
from app.application.services.ApplicationUserApplication import ApplicationUserApplication
from app.infrastructure.repositories.RoleRepository import RoleRepository
from app.domain.dtos.WordpressUserDto import WordpressUserResponseDto
from app.infrastructure.db.wordpressConnection import getWordpressDb
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/application-user", tags=["application-user"])

def getApplicationUserApplication(db: Session = Depends(getDb), wpDb: Session = Depends(getWordpressDb)) -> IApplicationUserApplication:
    applicationUserRepository = ApplicationUserRepository(db)
    roleRepository = RoleRepository(db)
    wordpressUserRepository = WordpressUserRepository(wpDb)
    return ApplicationUserApplication(applicationUserRepository, roleRepository, wordpressUserRepository)

@router.get("/wordpress-users", response_model=apiResponseDto[List[WordpressUserResponseDto]])
def searchWordpressUsers(search: str = Query(...), service: IApplicationUserApplication = Depends(getApplicationUserApplication)):
    try:
        data = service.searchWordpressUsers(search)
        return apiResponseDto(isSuccess=True, Message="Usuarios de WordPress obtenidos correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        print("ERROR REAL BUSCANDO USUARIOS WORDPRESS:", repr(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al buscar usuarios de WordPress: {str(e)}")

@router.get("/", response_model=apiResponseDto[List[ApplicationUserResponseDto]])
def getAllApplicationUsers(service: IApplicationUserApplication = Depends(getApplicationUserApplication)):
    try:
        data = service.getAll()

        if not data:
            return apiResponseDto(isSuccess=False, Message="No existen usuarios del aplicativo registrados.", result=[])
        
        return apiResponseDto(isSuccess=True, Message="Usuarios del aplicativo obtenidos correctamente.", result=data)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los usuarios del aplicativo.")

@router.get("/{IdApplicationUser}", response_model=apiResponseDto[ApplicationUserResponseDto])
def getApplicationUserById(IdApplicationUser: int, service: IApplicationUserApplication = Depends(getApplicationUserApplication)):
    try:
        data = service.getById(IdApplicationUser)
        return apiResponseDto(isSuccess=True, Message="Usuario del aplicativo obtenido correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el usuario del aplicativo.")

@router.post("/", response_model=apiResponseDto[ApplicationUserResponseDto], status_code=status.HTTP_201_CREATED)
def createApplicationUser(applicationUserData: ApplicationUserCreateDto, service: IApplicationUserApplication = Depends(getApplicationUserApplication)):
    try:
        data = service.create(applicationUserData)
        return apiResponseDto(isSuccess=True, Message="Usuario autorizado correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al autorizar el usuario.")

@router.put("/{IdApplicationUser}", response_model=apiResponseDto[ApplicationUserResponseDto])
def updateApplicationUser(IdApplicationUser: int, applicationUserData: ApplicationUserUpdateDto, service: IApplicationUserApplication = Depends(getApplicationUserApplication)):
    try:
        data = service.update(IdApplicationUser, applicationUserData)
        return apiResponseDto(isSuccess=True, Message="Usuario del aplicativo actualizado correctamente.", result=data)

    except ValueError as e:
        message = str(e)
        statusCode = status.HTTP_404_NOT_FOUND if "no encontrado" in message.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el usuario del aplicativo.")

@router.delete("/{IdApplicationUser}", response_model=apiResponseDto[dict])
def deleteApplicationUser(IdApplicationUser: int, service: IApplicationUserApplication = Depends(getApplicationUserApplication)):
    try:
        service.delete(IdApplicationUser)
        return apiResponseDto(isSuccess=True, Message="Usuario del aplicativo eliminado correctamente.", result={})

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el usuario del aplicativo.")