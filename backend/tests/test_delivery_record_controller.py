from app.domain.dtos.DeliveryRecordDto import DeliveryRecordResponseDto
from app.api import deliveryRecordController as ctl
from app.api import authController as auth_ctl
from datetime import date, datetime, timezone
from fastapi.testclient import TestClient
from collections.abc import Generator
from unittest.mock import MagicMock
import pytest
from fastapi import FastAPI

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

def _record() -> DeliveryRecordResponseDto:
    return DeliveryRecordResponseDto(
        IdDeliveryRecord=1,
        deliveryDate=date(2026, 1, 10),
        IdPointSale=1,
        IdDomiciliary=2,
        deliveryQuantity=5,
        IdAbsenceType=None,
        absenceType=None,
        createdByDeliveryRecord="u",
        createdAtDeliveryRecord=datetime(2026, 1, 10, tzinfo=timezone.utc),
        updatedByDeliveryRecord=None,
        updatedAtDeliveryRecord=None,
        settlement=None,
    )

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer x"}

def test_get_all_empty(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getAll.return_value = []
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/delivery-record/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["isSuccess"] is False

def test_get_all_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getAll.return_value = [_record()]
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/delivery-record/", headers=auth_headers)
    assert r.status_code == 200

def test_get_by_id_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getById.return_value = _record()
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/delivery-record/1", headers=auth_headers)
    assert r.status_code == 200

def test_get_by_id_not_found(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getById.side_effect = ValueError("no")
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get("/delivery-record/1", headers=auth_headers)
    assert r.status_code == 404

def test_create_missing_user_reference(client: TestClient, auth_headers):
    svc = MagicMock()
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {}

    body = {"deliveryDate": "2026-01-10", "IdPointSale": 1, "IdDomiciliary": 2, "deliveryQuantity": 1}
    r = client.post("/delivery-record/", headers=auth_headers, json=body)
    assert r.status_code == 401

def test_create_success_wordpress(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.create.return_value = _record()
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    body = {"deliveryDate": "2026-01-10", "IdPointSale": 1, "IdDomiciliary": 2, "deliveryQuantity": 1}
    r = client.post("/delivery-record/", headers=auth_headers, json=body)
    assert r.status_code == 201

def test_create_success_point_sale_email(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.create.return_value = _record()
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {
        "authType": "POINT_SALE_EMAIL",
        "pointSaleEmail": "pv@example.com",
    }

    body = {"deliveryDate": "2026-01-10", "IdPointSale": 1, "IdDomiciliary": 2, "deliveryQuantity": 1}
    r = client.post("/delivery-record/", headers=auth_headers, json=body)
    assert r.status_code == 201

def test_create_validation(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.create.side_effect = ValueError("bad")
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    body = {"deliveryDate": "2026-01-10", "IdPointSale": 1, "IdDomiciliary": 2}
    r = client.post("/delivery-record/", headers=auth_headers, json=body)
    assert r.status_code == 400

def test_bulk_create_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.createMany.return_value = [_record()]
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    body = {
        "deliveryDate": "2026-01-10",
        "IdPointSale": 1,
        "records": [{"IdDomiciliary": 2, "deliveryQuantity": 1}],
    }
    r = client.post("/delivery-record/bulk", headers=auth_headers, json=body)
    assert r.status_code == 201

def test_update_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.update.return_value = _record()
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.put("/delivery-record/1", headers=auth_headers, json={"deliveryQuantity": 2})
    assert r.status_code == 200

def test_update_not_found_message(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.update.side_effect = ValueError("no encontrado en sistema")
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.put("/delivery-record/1", headers=auth_headers, json={"deliveryQuantity": 2})
    assert r.status_code == 404

def test_delete_success(client: TestClient, auth_headers):
    svc = MagicMock()
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.delete("/delivery-record/1", headers=auth_headers)
    assert r.status_code == 200

def test_delete_not_found(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.delete.side_effect = ValueError("no")
    client.app.dependency_overrides[ctl.getDeliveryRecordApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.delete("/delivery-record/1", headers=auth_headers)
    assert r.status_code == 404