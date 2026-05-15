from app.domain.dtos.DomiciliaryDto import DomiciliaryResponseDto
from app.api import domiciliaryController as ctl
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

def _dom() -> DomiciliaryResponseDto:
    return DomiciliaryResponseDto(IdDomiciliary=1, documentDomiciliary="123", nameDomiciliary="D", statusDomiciliary=True, pointSale=1,)

def test_get_all_empty(client: TestClient):
    svc = MagicMock()
    svc.getAll.return_value = []
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    r = client.get("/domiciliary/")
    assert r.status_code == 200
    assert r.json()["isSuccess"] is False

def test_get_all_success(client: TestClient):
    svc = MagicMock()
    svc.getAll.return_value = [_dom()]
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    r = client.get("/domiciliary/", params={"pointSale": 1, "statusDomiciliary": True})
    assert r.status_code == 200

def test_get_all_value_error_404(client: TestClient):
    svc = MagicMock()
    svc.getAll.side_effect = ValueError("no pv")
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    r = client.get("/domiciliary/")
    assert r.status_code == 404

def test_get_by_id_success(client: TestClient):
    svc = MagicMock()
    svc.getById.return_value = _dom()
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    r = client.get("/domiciliary/1")
    assert r.status_code == 200

def test_get_by_id_not_found(client: TestClient):
    svc = MagicMock()
    svc.getById.side_effect = ValueError("no")
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    r = client.get("/domiciliary/1")
    assert r.status_code == 404

def test_get_by_document_success(client: TestClient):
    svc = MagicMock()
    svc.getByDocument.return_value = _dom()
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    r = client.get("/domiciliary/document/123")
    assert r.status_code == 200

def test_get_by_point_sale_empty(client: TestClient):
    svc = MagicMock()
    svc.getByPointSale.return_value = []
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    r = client.get("/domiciliary/pointSale/1")
    assert r.status_code == 200
    assert r.json()["isSuccess"] is False

def test_get_by_point_sale_success(client: TestClient):
    svc = MagicMock()
    svc.getByPointSale.return_value = [_dom()]
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    r = client.get("/domiciliary/pointSale/1")
    assert r.status_code == 200

def test_create_success(client: TestClient):
    svc = MagicMock()
    svc.create.return_value = _dom()
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    body = {
        "documentDomiciliary": "123",
        "nameDomiciliary": "D",
        "statusDomiciliary": True,
        "pointSale": 1,
    }
    r = client.post("/domiciliary/", json=body)
    assert r.status_code == 201

def test_create_validation(client: TestClient):
    svc = MagicMock()
    svc.create.side_effect = ValueError("dup")
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    body = {
        "documentDomiciliary": "123",
        "nameDomiciliary": "D",
        "statusDomiciliary": True,
        "pointSale": 1,
    }
    r = client.post("/domiciliary/", json=body)
    assert r.status_code == 400

def test_update_success(client: TestClient):
    svc = MagicMock()
    svc.update.return_value = _dom()
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    r = client.put("/domiciliary/1", json={"nameDomiciliary": "X"})
    assert r.status_code == 200

def test_update_not_found(client: TestClient):
    svc = MagicMock()
    svc.update.side_effect = ValueError("no encontrado")
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    r = client.put("/domiciliary/1", json={"nameDomiciliary": "X"})
    assert r.status_code == 404

def test_delete_success(client: TestClient):
    svc = MagicMock()
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    r = client.delete("/domiciliary/1")
    assert r.status_code == 200

def test_delete_not_found(client: TestClient):
    svc = MagicMock()
    svc.delete.side_effect = ValueError("no")
    client.app.dependency_overrides[ctl.getDomiciliaryApplication] = lambda: svc

    r = client.delete("/domiciliary/1")
    assert r.status_code == 404