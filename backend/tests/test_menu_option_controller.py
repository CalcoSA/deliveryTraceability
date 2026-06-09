from app.domain.dtos.MenuOptionDto import MenuOptionResponseDto
from app.api import menuOptionController as ctl
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

def _mo() -> MenuOptionResponseDto:
    return MenuOptionResponseDto(IdMenuOption=1, nameMenuOption="Home", pathMenuOption="/", iconMenuOption=None, parentMenuOption=None, orderMenuOption=0, statusMenuOption=True,)

def test_get_all_success(client: TestClient):
    svc = MagicMock()
    svc.getAll.return_value = [_mo()]
    client.app.dependency_overrides[ctl.getMenuOptionApplication] = lambda: svc

    r = client.get("/menu-option/")
    assert r.status_code == 200

def test_get_all_server_error(client: TestClient):
    svc = MagicMock()
    svc.getAll.side_effect = RuntimeError()
    client.app.dependency_overrides[ctl.getMenuOptionApplication] = lambda: svc

    r = client.get("/menu-option/")
    assert r.status_code == 500

def test_get_by_id_success(client: TestClient):
    svc = MagicMock()
    svc.getById.return_value = _mo()
    client.app.dependency_overrides[ctl.getMenuOptionApplication] = lambda: svc

    r = client.get("/menu-option/1")
    assert r.status_code == 200

def test_get_by_id_not_found(client: TestClient):
    svc = MagicMock()
    svc.getById.side_effect = ValueError("no")
    client.app.dependency_overrides[ctl.getMenuOptionApplication] = lambda: svc

    r = client.get("/menu-option/1")
    assert r.status_code == 404

def test_create_success(client: TestClient):
    svc = MagicMock()
    svc.create.return_value = _mo()
    client.app.dependency_overrides[ctl.getMenuOptionApplication] = lambda: svc

    r = client.post("/menu-option/", json={"nameMenuOption": "Home", "orderMenuOption": 0})
    assert r.status_code == 201

def test_create_validation(client: TestClient):
    svc = MagicMock()
    svc.create.side_effect = ValueError("bad")
    client.app.dependency_overrides[ctl.getMenuOptionApplication] = lambda: svc

    r = client.post("/menu-option/", json={"nameMenuOption": "Home", "orderMenuOption": 0})
    assert r.status_code == 400

def test_update_success(client: TestClient):
    svc = MagicMock()
    svc.update.return_value = _mo()
    client.app.dependency_overrides[ctl.getMenuOptionApplication] = lambda: svc

    r = client.put("/menu-option/1", json={"nameMenuOption": "X"})
    assert r.status_code == 200

def test_update_not_found_message(client: TestClient):
    svc = MagicMock()
    svc.update.side_effect = ValueError("Opción no encontrada")
    client.app.dependency_overrides[ctl.getMenuOptionApplication] = lambda: svc

    r = client.put("/menu-option/1", json={"nameMenuOption": "X"})
    assert r.status_code == 404

def test_update_bad_request_message(client: TestClient):
    svc = MagicMock()
    svc.update.side_effect = ValueError("invalid")
    client.app.dependency_overrides[ctl.getMenuOptionApplication] = lambda: svc

    r = client.put("/menu-option/1", json={"nameMenuOption": "X"})
    assert r.status_code == 400

def test_delete_success(client: TestClient):
    svc = MagicMock()
    client.app.dependency_overrides[ctl.getMenuOptionApplication] = lambda: svc

    r = client.delete("/menu-option/1")
    assert r.status_code == 200

def test_delete_not_found(client: TestClient):
    svc = MagicMock()
    svc.delete.side_effect = ValueError("no")
    client.app.dependency_overrides[ctl.getMenuOptionApplication] = lambda: svc

    r = client.delete("/menu-option/1")
    assert r.status_code == 404