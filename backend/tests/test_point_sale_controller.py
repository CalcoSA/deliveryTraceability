from app.domain.dtos.pointSaleDto import pointSaleResponseDto
from app.api import pointSaleController as ctl
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

def _ps() -> pointSaleResponseDto:
    return pointSaleResponseDto(IdPointSale=1, codePointSale="C", namePointSale="N", statusPointSale=True)

def test_get_all_empty(client: TestClient):
    svc = MagicMock()
    svc.getAll.return_value = []
    client.app.dependency_overrides[ctl.getPointSaleApplication] = lambda: svc

    r = client.get("/pointSale/")
    assert r.status_code == 200
    assert r.json()["isSuccess"] is False

def test_get_all_success(client: TestClient):
    svc = MagicMock()
    svc.getAll.return_value = [_ps()]
    client.app.dependency_overrides[ctl.getPointSaleApplication] = lambda: svc

    r = client.get("/pointSale/")
    assert r.status_code == 200

def test_get_by_id_success(client: TestClient):
    svc = MagicMock()
    svc.getById.return_value = _ps()
    client.app.dependency_overrides[ctl.getPointSaleApplication] = lambda: svc

    r = client.get("/pointSale/1")
    assert r.status_code == 200

def test_get_by_id_not_found(client: TestClient):
    svc = MagicMock()
    svc.getById.return_value = None
    client.app.dependency_overrides[ctl.getPointSaleApplication] = lambda: svc

    r = client.get("/pointSale/1")
    assert r.status_code == 404

def test_create_success(client: TestClient):
    svc = MagicMock()
    svc.create.return_value = _ps()
    client.app.dependency_overrides[ctl.getPointSaleApplication] = lambda: svc

    r = client.post("/pointSale/", json={"codePointSale": "C", "namePointSale": "N", "statusPointSale": True})
    assert r.status_code == 201

def test_create_validation(client: TestClient):
    svc = MagicMock()
    svc.create.side_effect = ValueError("dup")
    client.app.dependency_overrides[ctl.getPointSaleApplication] = lambda: svc

    r = client.post("/pointSale/", json={"codePointSale": "C", "namePointSale": "N", "statusPointSale": True})
    assert r.status_code == 400

def test_update_success(client: TestClient):
    svc = MagicMock()
    svc.update.return_value = _ps()
    client.app.dependency_overrides[ctl.getPointSaleApplication] = lambda: svc

    r = client.put("/pointSale/1", json={"namePointSale": "X"})
    assert r.status_code == 200

def test_update_not_found(client: TestClient):
    svc = MagicMock()
    svc.update.return_value = None
    client.app.dependency_overrides[ctl.getPointSaleApplication] = lambda: svc

    r = client.put("/pointSale/1", json={"namePointSale": "X"})
    assert r.status_code == 404

def test_delete_success(client: TestClient):
    svc = MagicMock()
    svc.delete.return_value = True
    client.app.dependency_overrides[ctl.getPointSaleApplication] = lambda: svc

    r = client.delete("/pointSale/1")
    assert r.status_code == 200

def test_delete_not_found(client: TestClient):
    svc = MagicMock()
    svc.delete.return_value = False
    client.app.dependency_overrides[ctl.getPointSaleApplication] = lambda: svc

    r = client.delete("/pointSale/1")
    assert r.status_code == 404