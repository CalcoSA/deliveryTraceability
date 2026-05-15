from app.domain.dtos.PointSaleEmailDto import PointSaleEmailResponseDto
from app.api import pointSaleEmailController as ctl
from app.api import authController as auth_ctl
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

def _row() -> PointSaleEmailResponseDto:
    return PointSaleEmailResponseDto(IdPointSaleEmail=1, emailPointSale="pv@example.com", statusPointSaleEmail=True, createdAtPointSaleEmail=datetime(2026, 1, 1, tzinfo=timezone.utc), updatedAtPointSaleEmail=None,)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer x"}

def test_get_all_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getAll.return_value = [_row()]
    client.app.dependency_overrides[ctl.getPointSaleEmailApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/point-sale-email/", headers=auth_headers)
    assert r.status_code == 200

def test_get_all_server_error(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getAll.side_effect = RuntimeError()
    client.app.dependency_overrides[ctl.getPointSaleEmailApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/point-sale-email/", headers=auth_headers)
    assert r.status_code == 500

def test_create_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.create.return_value = _row()
    client.app.dependency_overrides[ctl.getPointSaleEmailApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.post("/point-sale-email/", headers=auth_headers, json={"emailPointSale": "pv@example.com"})
    assert r.status_code == 201

def test_create_validation(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.create.side_effect = ValueError("dup")
    client.app.dependency_overrides[ctl.getPointSaleEmailApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.post("/point-sale-email/", headers=auth_headers, json={"emailPointSale": "pv@example.com"})
    assert r.status_code == 400

def test_update_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.update.return_value = _row()
    client.app.dependency_overrides[ctl.getPointSaleEmailApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.put("/point-sale-email/1", headers=auth_headers, json={"statusPointSaleEmail": False})
    assert r.status_code == 200

def test_update_not_found(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.update.side_effect = ValueError("Correo no encontrado")
    client.app.dependency_overrides[ctl.getPointSaleEmailApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.put("/point-sale-email/1", headers=auth_headers, json={"statusPointSaleEmail": False})
    assert r.status_code == 404

def test_delete_success(client: TestClient, auth_headers):
    svc = MagicMock()
    client.app.dependency_overrides[ctl.getPointSaleEmailApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.delete("/point-sale-email/1", headers=auth_headers)
    assert r.status_code == 200

def test_delete_not_found(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.delete.side_effect = ValueError("no")
    client.app.dependency_overrides[ctl.getPointSaleEmailApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.delete("/point-sale-email/1", headers=auth_headers)
    assert r.status_code == 404