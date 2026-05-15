from app.domain.dtos.AuthDto import AuthResponseDto, AuthUserDto
from fastapi.testclient import TestClient
from app.api import authController as ac
from collections.abc import Generator
from unittest.mock import MagicMock
from fastapi import FastAPI
import pytest

def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(ac.router)
    return app

def _auth_user(**kwargs) -> AuthUserDto:
    base = dict(wordpressUserLogin="user", wordpressUserEmail="user@example.com", wordpressDisplayName="User Name", roles=[], menuOptions=[], wordpressUserId=1,)
    base.update(kwargs)
    return AuthUserDto(**base)

def _auth_response(**user_kwargs) -> AuthResponseDto:
    return AuthResponseDto(accessToken="tok", user=_auth_user(**user_kwargs))

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app = _app()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

def test_login_success(client: TestClient):
    svc = MagicMock()
    svc.login.return_value = _auth_response()
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.post("/auth/login", json={"username": "u", "password": "p"})
    assert r.status_code == 200
    body = r.json()
    assert body["isSuccess"] is True
    assert body["result"]["accessToken"] == "tok"

def test_login_value_error_401(client: TestClient):
    svc = MagicMock()
    svc.login.side_effect = ValueError("bad creds")
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.post("/auth/login", json={"username": "u", "password": "p"})
    assert r.status_code == 401
    assert r.json()["detail"] == "bad creds"

def test_login_permission_error_403(client: TestClient):
    svc = MagicMock()
    svc.login.side_effect = PermissionError("forbidden")
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.post("/auth/login", json={"username": "u", "password": "p"})
    assert r.status_code == 403

def test_login_unexpected_error_500_prod_detail(client: TestClient, monkeypatch):
    monkeypatch.setattr(ac, "APP_ENV", "production")
    svc = MagicMock()
    svc.login.side_effect = RuntimeError("boom")
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.post("/auth/login", json={"username": "u", "password": "p"})
    assert r.status_code == 500
    assert r.json()["detail"] == "Error al iniciar sesión."

def test_login_unexpected_error_500_dev_detail(client: TestClient, monkeypatch):
    monkeypatch.setattr(ac, "APP_ENV", "development")
    svc = MagicMock()
    svc.login.side_effect = RuntimeError("boom")
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.post("/auth/login", json={"username": "u", "password": "p"})
    assert r.status_code == 500
    assert "boom" in r.json()["detail"]

def test_intranet_access_success(client: TestClient):
    svc = MagicMock()
    svc.intranetAccess.return_value = _auth_response()
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.get("/auth/intranet-access", params={"userLogin": "u", "ts": 1, "sig": "s"})
    assert r.status_code == 200
    assert r.json()["isSuccess"] is True

def test_intranet_access_permission_error(client: TestClient):
    svc = MagicMock()
    svc.intranetAccess.side_effect = PermissionError("no")
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.get("/auth/intranet-access", params={"userLogin": "u", "ts": 1, "sig": "s"})
    assert r.status_code == 403

def test_intranet_access_500_qa_detail(client: TestClient, monkeypatch):
    monkeypatch.setattr(ac, "APP_ENV", "qa")
    svc = MagicMock()
    svc.intranetAccess.side_effect = RuntimeError("x")
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.get("/auth/intranet-access", params={"userLogin": "u", "ts": 1, "sig": "s"})
    assert r.status_code == 500
    assert "x" in r.json()["detail"]

def test_me_wordpress_user(client: TestClient):
    svc = MagicMock()
    svc.getCurrentUser.return_value = _auth_response()
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc
    client.app.dependency_overrides[ac.getCurrentPayload] = lambda: {"authType": "OTHER", "wordpressUserId": 9}

    r = client.get("/auth/me", headers={"Authorization": "Bearer ignored"})
    assert r.status_code == 200
    svc.getCurrentUser.assert_called_once_with(9)

def test_me_point_sale_email(client: TestClient):
    svc = MagicMock()
    svc.getCurrentPointSaleEmailUser.return_value = _auth_response(pointSaleEmailId=3)
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc
    client.app.dependency_overrides[ac.getCurrentPayload] = lambda: {"authType": "POINT_SALE_EMAIL", "pointSaleEmailId": 3}

    r = client.get("/auth/me", headers={"Authorization": "Bearer ignored"})
    assert r.status_code == 200
    svc.getCurrentPointSaleEmailUser.assert_called_once_with(3)

def test_me_permission_error(client: TestClient):
    svc = MagicMock()
    svc.getCurrentUser.side_effect = PermissionError("denied")
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc
    client.app.dependency_overrides[ac.getCurrentPayload] = lambda: {"authType": "X", "wordpressUserId": 1}

    r = client.get("/auth/me", headers={"Authorization": "Bearer x"})
    assert r.status_code == 403

def test_me_unexpected_error(client: TestClient):
    svc = MagicMock()
    svc.getCurrentUser.side_effect = RuntimeError()
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc
    client.app.dependency_overrides[ac.getCurrentPayload] = lambda: {"authType": "X", "wordpressUserId": 1}

    r = client.get("/auth/me", headers={"Authorization": "Bearer x"})
    assert r.status_code == 500

def test_request_point_sale_email_code_success(client: TestClient):
    svc = MagicMock()
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.post("/auth/point-sale/request-code", json={"emailPointSale": "a@b.co"})
    assert r.status_code == 200
    svc.requestPointSaleEmailCode.assert_called_once_with("a@b.co")

def test_request_point_sale_email_code_value_error(client: TestClient):
    svc = MagicMock()
    svc.requestPointSaleEmailCode.side_effect = ValueError("invalid")
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.post("/auth/point-sale/request-code", json={"emailPointSale": "a@b.co"})
    assert r.status_code == 400

def test_request_point_sale_email_code_server_error(client: TestClient):
    svc = MagicMock()
    svc.requestPointSaleEmailCode.side_effect = RuntimeError()
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.post("/auth/point-sale/request-code", json={"emailPointSale": "a@b.co"})
    assert r.status_code == 500

def test_verify_point_sale_email_code_success(client: TestClient):
    svc = MagicMock()
    svc.verifyPointSaleEmailCode.return_value = _auth_response()
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.post(
        "/auth/point-sale/verify-code",
        json={"emailPointSale": "a@b.co", "code": "123456"},
    )
    assert r.status_code == 200

def test_verify_point_sale_email_code_value_error(client: TestClient):
    svc = MagicMock()
    svc.verifyPointSaleEmailCode.side_effect = ValueError("bad")
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.post(
        "/auth/point-sale/verify-code",
        json={"emailPointSale": "a@b.co", "code": "1"},
    )
    assert r.status_code == 400

def test_verify_point_sale_email_code_permission_error(client: TestClient):
    svc = MagicMock()
    svc.verifyPointSaleEmailCode.side_effect = PermissionError("no")
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.post(
        "/auth/point-sale/verify-code",
        json={"emailPointSale": "a@b.co", "code": "1"},
    )
    assert r.status_code == 403

def test_verify_point_sale_email_code_server_error(client: TestClient):
    svc = MagicMock()
    svc.verifyPointSaleEmailCode.side_effect = RuntimeError()
    client.app.dependency_overrides[ac.getAuthApplication] = lambda: svc

    r = client.post(
        "/auth/point-sale/verify-code",
        json={"emailPointSale": "a@b.co", "code": "1"},
    )
    assert r.status_code == 500