from fastapi import status

from app.core.constants import INCORRECT_CURRENT_PASSWORD
from app.core.security import verify_password
from app.db.models import Users

from .utils import client, TestingSessionLocal, TEST_USER_PASSWORD


def get_user_from_db(user_id):
    db = TestingSessionLocal()
    try:
        return db.query(Users).filter(Users.id == user_id).first()
    finally:
        db.close()


def test_get_me(test_user):
    response = client.get("/user/me")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["role"] == test_user.role
    assert "hashed_password" not in data  # response_model must hide the hash


def test_change_password(test_user):
    payload = {"current_password": TEST_USER_PASSWORD, "new_password": "newpassword123"}
    response = client.put("/user/change-password", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert verify_password("newpassword123", get_user_from_db(test_user.id).hashed_password)


def test_change_password_wrong_current_password(test_user):
    payload = {"current_password": "wrongpassword", "new_password": "newpassword123"}
    response = client.put("/user/change-password", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": INCORRECT_CURRENT_PASSWORD}
    assert verify_password(TEST_USER_PASSWORD, get_user_from_db(test_user.id).hashed_password)


def test_change_password_same_as_current():
    payload = {"current_password": TEST_USER_PASSWORD, "new_password": TEST_USER_PASSWORD}
    response = client.put("/user/change-password", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_change_password_too_short():
    payload = {"current_password": TEST_USER_PASSWORD, "new_password": "abc"}
    response = client.put("/user/change-password", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
