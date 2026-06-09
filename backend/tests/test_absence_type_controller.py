from app.domain.dtos.AbsenceTypeDto import AbsenceTypeResponseDto
from app.api import absenceTypeController as ctl
from app.api import authController as auth_ctl
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

def _abs() -> AbsenceTypeResponseDto:
    return AbsenceTypeResponseDto(IdAbsenceType=1, nameAbsenceType="Vacaciones", statusAbsenceType=True)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer x"}

def test_get_all_empty(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getAllActive.return_value = []
    client.app.dependency_overrides[ctl.getAbsenceTypeApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/absence-type/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["isSuccess"] is False

def test_get_all_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getAllActive.return_value = [_abs()]
    client.app.dependency_overrides[ctl.getAbsenceTypeApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/absence-type/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["isSuccess"] is True

def test_get_all_server_error(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getAllActive.side_effect = RuntimeError()
    client.app.dependency_overrides[ctl.getAbsenceTypeApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/absence-type/", headers=auth_headers)
    assert r.status_code == 500