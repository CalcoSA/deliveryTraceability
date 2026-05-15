from app.domain.dtos.ParameterDto import ParameterHistoryResponseDto, ParameterResponseDto
from app.api import authController as auth_ctl
from app.api import parameterController as ctl
from fastapi.testclient import TestClient
from datetime import datetime, timezone
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

def _param() -> ParameterResponseDto:
    return ParameterResponseDto(IdParameter=1, nameParameter="n", valueParameter="v", createdByParameter="u", createdAtParameter=datetime(2026, 1, 1, tzinfo=timezone.utc), updatedByParameter=None, updatedAtParameter=None,)

def _hist() -> ParameterHistoryResponseDto:
    return ParameterHistoryResponseDto(IdParameterHistory=1, IdParameter=1, actionParameterHistory="UPDATE", previousNameParameter=None, newNameParameter=None, previousValueParameter=None, newValueParameter=None, createdByParameterHistory="u", createdAtParameterHistory=datetime(2026, 1, 2, tzinfo=timezone.utc),)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer x"}

def test_get_all_parameters_empty(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getAll.return_value = []
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/parameter/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["isSuccess"] is False

def test_get_all_parameters_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getAll.return_value = [_param()]
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/parameter/", headers=auth_headers)
    assert r.status_code == 200

def test_get_parameter_by_id_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getById.return_value = _param()
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/parameter/1", headers=auth_headers)
    assert r.status_code == 200

def test_get_parameter_by_id_not_found(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getById.side_effect = ValueError("no")
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/parameter/1", headers=auth_headers)
    assert r.status_code == 404

def test_get_parameter_history_empty(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getHistoryByParameterId.return_value = []
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/parameter/1/history", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["isSuccess"] is False

def test_get_parameter_history_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getHistoryByParameterId.return_value = [_hist()]
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/parameter/1/history", headers=auth_headers)
    assert r.status_code == 200

def test_create_parameter_missing_login(client: TestClient, auth_headers):
    svc = MagicMock()
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {}

    r = client.post("/parameter/", headers=auth_headers, json={"nameParameter": "a", "valueParameter": "b"})
    assert r.status_code == 401

def test_create_parameter_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.create.return_value = _param()
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.post("/parameter/", headers=auth_headers, json={"nameParameter": "a", "valueParameter": "b"})
    assert r.status_code == 201

def test_create_parameter_validation(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.create.side_effect = ValueError("bad")
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.post("/parameter/", headers=auth_headers, json={"nameParameter": "a", "valueParameter": "b"})
    assert r.status_code == 400

def test_update_parameter_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.update.return_value = _param()
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.put("/parameter/1", headers=auth_headers, json={"valueParameter": "x"})
    assert r.status_code == 200

def test_update_parameter_not_found(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.update.side_effect = ValueError("Parámetro no encontrado")
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.put("/parameter/1", headers=auth_headers, json={"valueParameter": "x"})
    assert r.status_code == 404

def test_delete_parameter_success(client: TestClient, auth_headers):
    svc = MagicMock()
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.delete("/parameter/1", headers=auth_headers)
    assert r.status_code == 200

def test_delete_parameter_not_found(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.delete.side_effect = ValueError("no")
    client.app.dependency_overrides[ctl.getParameterApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.delete("/parameter/1", headers=auth_headers)
    assert r.status_code == 404