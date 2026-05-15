from app.domain.dtos.DeliveryReportDto import DeliverySettlementReportResponseDto
from app.api import deliveryReportController as ctl
from app.api import authController as auth_ctl
from fastapi.testclient import TestClient
from collections.abc import Generator
from unittest.mock import MagicMock
from decimal import Decimal
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

def _row() -> DeliverySettlementReportResponseDto:
    return DeliverySettlementReportResponseDto(
        periodType="day",
        periodKey="2026-01-10",
        periodLabel="2026-01-10",
        IdPointSale=1,
        codePointSale="C",
        namePointSale="PV",
        IdDomiciliary=2,
        documentDomiciliary="123",
        nameDomiciliary="D",
        parameterNameSettlement="fee",
        parameterValueSettlement=Decimal("1000"),
        totalDeliveryQuantity=10,
        totalAbsences=0,
        absenceTypes="",
        totalValueSettlement=Decimal("10000"),
        totalRecords=1,
        createdByUsers="u",
    )

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer x"}

def test_settlement_report_empty(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getSettlementReport.return_value = []
    client.app.dependency_overrides[ctl.getDeliveryReportApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get(
        "/delivery-report/settlement",
        headers=auth_headers,
        params={"startDate": "2026-01-01", "endDate": "2026-01-31"},
    )
    assert r.status_code == 200
    assert r.json()["isSuccess"] is False

def test_settlement_report_success(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getSettlementReport.return_value = [_row()]
    client.app.dependency_overrides[ctl.getDeliveryReportApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get(
        "/delivery-report/settlement",
        headers=auth_headers,
        params={"startDate": "2026-01-01", "endDate": "2026-01-31", "period": "day", "IdPointSale": 1},
    )
    assert r.status_code == 200
    assert r.json()["isSuccess"] is True

def test_settlement_report_value_error(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getSettlementReport.side_effect = ValueError("bad period")
    client.app.dependency_overrides[ctl.getDeliveryReportApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get(
        "/delivery-report/settlement",
        headers=auth_headers,
        params={"startDate": "2026-01-01", "endDate": "2026-01-31"},
    )
    assert r.status_code == 400

def test_settlement_report_server_error(client: TestClient, auth_headers):
    svc = MagicMock()
    svc.getSettlementReport.side_effect = RuntimeError()
    client.app.dependency_overrides[ctl.getDeliveryReportApplication] = lambda: svc
    client.app.dependency_overrides[auth_ctl.getCurrentPayload] = lambda: {"wordpressUserLogin": "u"}

    r = client.get(
        "/delivery-report/settlement",
        headers=auth_headers,
        params={"startDate": "2026-01-01", "endDate": "2026-01-31"},
    )
    assert r.status_code == 500