from app.domain.dtos.ApplicationUserDto import ApplicationUserResponseDto
from app.domain.dtos.WordpressUserDto import WordpressUserResponseDto
from app.api import applicationUserController as ctl
from app.domain.dtos.RoleDto import RoleResponseDto
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

def _sample_application_user() -> ApplicationUserResponseDto:
    return ApplicationUserResponseDto(IdApplicationUser=1, wordpressUserId=2, wordpressUserLogin="wp", statusApplicationUser=True, roles=[RoleResponseDto(IdRole=1, nameRole="Admin", statusRole=True)],)

def test_search_wordpress_users_success(client: TestClient):
    svc = MagicMock()
    svc.searchWordpressUsers.return_value = [
        WordpressUserResponseDto(wordpressUserId=1, wordpressUserLogin="l", wordpressUserEmail="e@e.com", wordpressDisplayName="N",)
    ]
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.get("/application-user/wordpress-users", params={"search": "ab"})
    assert r.status_code == 200
    assert r.json()["isSuccess"] is True

def test_search_wordpress_users_value_error(client: TestClient):
    svc = MagicMock()
    svc.searchWordpressUsers.side_effect = ValueError("invalid")
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.get("/application-user/wordpress-users", params={"search": "x"})
    assert r.status_code == 400

def test_search_wordpress_users_server_error(client: TestClient):
    svc = MagicMock()
    svc.searchWordpressUsers.side_effect = RuntimeError("db")
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.get("/application-user/wordpress-users", params={"search": "x"})
    assert r.status_code == 500

def test_get_all_empty(client: TestClient):
    svc = MagicMock()
    svc.getAll.return_value = []
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.get("/application-user/")
    assert r.status_code == 200
    assert r.json()["isSuccess"] is False

def test_get_all_success(client: TestClient):
    svc = MagicMock()
    svc.getAll.return_value = [_sample_application_user()]
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.get("/application-user/")
    assert r.status_code == 200
    assert r.json()["isSuccess"] is True

def test_get_by_id_success(client: TestClient):
    svc = MagicMock()
    svc.getById.return_value = _sample_application_user()
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.get("/application-user/1")
    assert r.status_code == 200

def test_get_by_id_not_found(client: TestClient):
    svc = MagicMock()
    svc.getById.side_effect = ValueError("no encontrado")
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.get("/application-user/99")
    assert r.status_code == 404

def test_create_success(client: TestClient):
    svc = MagicMock()
    svc.create.return_value = _sample_application_user()
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.post(
        "/application-user/",
        json={
            "wordpressUserId": 2,
            "wordpressUserLogin": "wp",
            "statusApplicationUser": True,
            "roleIds": [1],
        },
    )
    assert r.status_code == 201

def test_create_validation_error(client: TestClient):
    svc = MagicMock()
    svc.create.side_effect = ValueError("dup")
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.post(
        "/application-user/",
        json={"wordpressUserId": 2, "wordpressUserLogin": "wp", "roleIds": []},
    )
    assert r.status_code == 400

def test_update_success(client: TestClient):
    svc = MagicMock()
    svc.update.return_value = _sample_application_user()
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.put("/application-user/1", json={"statusApplicationUser": False})
    assert r.status_code == 200

def test_update_not_found_message(client: TestClient):
    svc = MagicMock()
    svc.update.side_effect = ValueError("Usuario no encontrado")
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.put("/application-user/1", json={"statusApplicationUser": True})
    assert r.status_code == 404

def test_update_bad_request_message(client: TestClient):
    svc = MagicMock()
    svc.update.side_effect = ValueError("invalid data")
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.put("/application-user/1", json={"statusApplicationUser": True})
    assert r.status_code == 400

def test_delete_success(client: TestClient):
    svc = MagicMock()
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.delete("/application-user/1")
    assert r.status_code == 200

def test_delete_not_found(client: TestClient):
    svc = MagicMock()
    svc.delete.side_effect = ValueError("missing")
    client.app.dependency_overrides[ctl.getApplicationUserApplication] = lambda: svc

    r = client.delete("/application-user/1")
    assert r.status_code == 404