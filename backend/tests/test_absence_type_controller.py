from app.api.absenceTypeController import (router, getAbsenceTypeApplication,)
from app.api.authController import getCurrentPayload
from fastapi.testclient import TestClient
from unittest.mock import Mock
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

def override_current_payload():
    return { "wordpressUserLogin": "juan.eusse", "IdApplicationUser": 1, "roleIds": [1], }

def test_get_all_absence_types_success_with_testclient():
    # Arrange
    fake_service = Mock()
    fake_service.getAllActive.return_value = [
        {
            "IdAbsenceType": 1,
            "nameAbsenceType": "Descanso",
            "statusAbsenceType": True,
        },
        {
            "IdAbsenceType": 2,
            "nameAbsenceType": "Vacaciones",
            "statusAbsenceType": True,
        },
    ]

    app.dependency_overrides[getCurrentPayload] = override_current_payload
    app.dependency_overrides[getAbsenceTypeApplication] = lambda: fake_service

    client = TestClient(app)

    # Act
    response = client.get("/absence-type/")

    # Assert
    assert response.status_code == 200

    body = response.json()

    assert body["isSuccess"] is True
    assert body["Message"] == "Tipos de ausentismo obtenidos correctamente."
    assert len(body["result"]) == 2
    assert body["result"][0]["nameAbsenceType"] == "Descanso"

    fake_service.getAllActive.assert_called_once()
    app.dependency_overrides.clear()

def test_get_all_absence_types_empty_with_testclient():
    # Arrange
    fake_service = Mock()
    fake_service.getAllActive.return_value = []

    app.dependency_overrides[getCurrentPayload] = override_current_payload
    app.dependency_overrides[getAbsenceTypeApplication] = lambda: fake_service

    client = TestClient(app)

    # Act
    response = client.get("/absence-type/")

    # Assert
    assert response.status_code == 200

    body = response.json()

    assert body["isSuccess"] is False
    assert body["Message"] == "No existen tipos de ausentismo activos."
    assert body["result"] == []

    fake_service.getAllActive.assert_called_once()
    app.dependency_overrides.clear()

def test_get_all_absence_types_unexpected_error_with_testclient():
    # Arrange
    fake_service = Mock()
    fake_service.getAllActive.side_effect = Exception("Error simulado")

    app.dependency_overrides[getCurrentPayload] = override_current_payload
    app.dependency_overrides[getAbsenceTypeApplication] = lambda: fake_service

    client = TestClient(app)

    # Act
    response = client.get("/absence-type/")

    # Assert
    assert response.status_code == 500

    body = response.json()

    assert body["detail"] == "Error al obtener los tipos de ausentismo."

    fake_service.getAllActive.assert_called_once()

    app.dependency_overrides.clear()