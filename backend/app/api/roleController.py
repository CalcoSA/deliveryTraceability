from app.domain.dtos.RoleDto import ( RoleCreateDto, RoleUpdateDto, RoleResponseDto, RoleDetailResponseDto, AssignMenuOptionsToRoleDto )
from app.infrastructure.repositories.MenuOptionRepository import MenuOptionRepository
from app.infrastructure.repositories.RoleRepository import RoleRepository
from app.application.interfaces.IRoleApplication import IRoleApplication
from app.application.services.RoleApplication import RoleApplication
from app.domain.dtos.MenuOptionDto import MenuOptionResponseDto
from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.dtos.apiResponseDto import apiResponseDto
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/role", tags=["role"])

def getRoleApplication(db: Session = Depends(getDb)) -> IRoleApplication:
    roleRepository = RoleRepository(db)
    menuOptionRepository = MenuOptionRepository(db)
    return RoleApplication(roleRepository, menuOptionRepository)

@router.get("/", response_model=apiResponseDto[List[RoleResponseDto]])
def getAllRoles(service: IRoleApplication = Depends(getRoleApplication)):
    try:
        data = service.getAll()

        if not data:
            return apiResponseDto(isSuccess=False, Message="No existen roles registrados.", result=[])
        
        return apiResponseDto(isSuccess=True, Message="Roles obtenidos correctamente.", result=data)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los roles.")

@router.get("/{IdRole}", response_model=apiResponseDto[RoleDetailResponseDto])
def getRoleById(IdRole: int, service: IRoleApplication = Depends(getRoleApplication)):
    try:
        role = service.getById(IdRole)
        menuOptions = service.getMenuOptionsByRole(IdRole)
        return apiResponseDto(
            isSuccess=True,
            Message="Rol obtenido correctamente.",
            result=RoleDetailResponseDto(
                IdRole=role.IdRole,
                nameRole=role.nameRole,
                statusRole=role.statusRole,
                menuOptions=menuOptions
            )
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el rol.")

@router.post("/", response_model=apiResponseDto[RoleResponseDto], status_code=status.HTTP_201_CREATED)
def createRole(roleData: RoleCreateDto, service: IRoleApplication = Depends(getRoleApplication)):
    try:
        data = service.create(roleData)
        return apiResponseDto(isSuccess=True, Message="Rol creado correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el rol.")

@router.put("/{IdRole}", response_model=apiResponseDto[RoleResponseDto])
def updateRole(IdRole: int, roleData: RoleUpdateDto, service: IRoleApplication = Depends(getRoleApplication)):
    try:
        data = service.update(IdRole, roleData)
        return apiResponseDto(isSuccess=True, Message="Rol actualizado correctamente.", result=data)

    except ValueError as e:
        message = str(e)
        statusCode = status.HTTP_404_NOT_FOUND if "no encontrado" in message.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el rol.")

@router.delete("/{IdRole}", response_model=apiResponseDto[dict])
def deleteRole(IdRole: int, service: IRoleApplication = Depends(getRoleApplication)):
    try:
        service.delete(IdRole)
        return apiResponseDto(isSuccess=True, Message="Rol eliminado correctamente.", result={})

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el rol.")

@router.get("/{IdRole}/menu-options", response_model=apiResponseDto[List[MenuOptionResponseDto]])
def getMenuOptionsByRole(IdRole: int, service: IRoleApplication = Depends(getRoleApplication)):
    try:
        data = service.getMenuOptionsByRole(IdRole)
        return apiResponseDto(isSuccess=True, Message="Opciones de menú del rol obtenidas correctamente.", result=data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener las opciones de menú del rol.")

@router.put("/{IdRole}/menu-options", response_model=apiResponseDto[List[MenuOptionResponseDto]])
def setMenuOptionsToRole(IdRole: int, data: AssignMenuOptionsToRoleDto, service: IRoleApplication = Depends(getRoleApplication)):
    try:
        result = service.setMenuOptionsToRole(IdRole, data.menuOptionIds)
        return apiResponseDto(isSuccess=True, Message="Opciones de menú asignadas correctamente al rol.", result=result)

    except ValueError as e:
        message = str(e)
        statusCode = status.HTTP_404_NOT_FOUND if "no encontrado" in message.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al asignar opciones de menú al rol.")