from app.domain.dtos.MenuOptionDto import MenuOptionResponseDto
from app.domain.dtos.RoleDto import RoleResponseDto
from app.api import roleController as ctl
from fastapi.testclient import TestClient
from collections.abc import Generator
from unittest.mock import MagicMock
from fastapi import FastAPI
import pytest

def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(ctl.router)
    return app

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app = _app()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

def _role() -> RoleResponseDto:
    return RoleResponseDto(IdRole=1, nameRole="R", statusRole=True)

def _menu() -> MenuOptionResponseDto:
    return MenuOptionResponseDto(IdMenuOption=1, nameMenuOption="M", pathMenuOption="/m", iconMenuOption=None, parentMenuOption=None, orderMenuOption=0, statusMenuOption=True,)

def test_get_all_roles_empty(client: TestClient):
    svc = MagicMock()
    svc.getAll.return_value = []
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.get("/role/")
    assert r.status_code == 200
    assert r.json()["isSuccess"] is False

def test_get_all_roles_success(client: TestClient):
    svc = MagicMock()
    svc.getAll.return_value = [_role()]
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.get("/role/")
    assert r.status_code == 200
    assert r.json()["isSuccess"] is True

def test_get_role_by_id_success(client: TestClient):
    svc = MagicMock()
    svc.getById.return_value = _role()
    svc.getMenuOptionsByRole.return_value = [_menu()]
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.get("/role/1")
    assert r.status_code == 200
    body = r.json()["result"]
    assert body["IdRole"] == 1
    assert len(body["menuOptions"]) == 1

def test_get_role_by_id_not_found(client: TestClient):
    svc = MagicMock()
    svc.getById.side_effect = ValueError("no")
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.get("/role/1")
    assert r.status_code == 404

def test_create_role_success(client: TestClient):
    svc = MagicMock()
    svc.create.return_value = _role()
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.post("/role/", json={"nameRole": "R", "statusRole": True, "menuOptionIds": []})
    assert r.status_code == 201

def test_create_role_validation(client: TestClient):
    svc = MagicMock()
    svc.create.side_effect = ValueError("bad")
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.post("/role/", json={"nameRole": "R", "menuOptionIds": []})
    assert r.status_code == 400

def test_update_role_success(client: TestClient):
    svc = MagicMock()
    svc.update.return_value = _role()
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.put("/role/1", json={"nameRole": "X"})
    assert r.status_code == 200

def test_update_role_not_found(client: TestClient):
    svc = MagicMock()
    svc.update.side_effect = ValueError("Rol no encontrado")
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.put("/role/1", json={"nameRole": "X"})
    assert r.status_code == 404

def test_delete_role_success(client: TestClient):
    svc = MagicMock()
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.delete("/role/1")
    assert r.status_code == 200

def test_delete_role_not_found(client: TestClient):
    svc = MagicMock()
    svc.delete.side_effect = ValueError("missing")
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.delete("/role/1")
    assert r.status_code == 404

def test_get_menu_options_by_role_success(client: TestClient):
    svc = MagicMock()
    svc.getMenuOptionsByRole.return_value = [_menu()]
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.get("/role/1/menu-options")
    assert r.status_code == 200

def test_get_menu_options_by_role_not_found(client: TestClient):
    svc = MagicMock()
    svc.getMenuOptionsByRole.side_effect = ValueError("no")
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.get("/role/1/menu-options")
    assert r.status_code == 404

def test_set_menu_options_to_role_success(client: TestClient):
    svc = MagicMock()
    svc.setMenuOptionsToRole.return_value = [_menu()]
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.put("/role/1/menu-options", json={"menuOptionIds": [1]})
    assert r.status_code == 200

def test_set_menu_options_to_role_not_found(client: TestClient):
    svc = MagicMock()
    svc.setMenuOptionsToRole.side_effect = ValueError("Rol no encontrado")
    client.app.dependency_overrides[ctl.getRoleApplication] = lambda: svc

    r = client.put("/role/1/menu-options", json={"menuOptionIds": [1]})
    assert r.status_code == 404