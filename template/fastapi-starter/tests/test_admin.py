from fastapi import status

from app.core.constants import INSUFFICIENT_PERMISSIONS, ITEM_NOT_FOUND, ROLE_USER
from app.db.models import Items, Users
from app.dependencies import get_current_user
from app.main import app

from .utils import client, TestingSessionLocal


def test_read_all_items(test_item):
    response = client.get("/admin/items")
    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.json()] == [test_item.id]


def test_delete_item(test_item):
    response = client.delete(f"/admin/items/{test_item.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    deleted_item = db.query(Items).filter(Items.id == test_item.id).first()
    db.close()
    assert deleted_item is None


def test_delete_item_not_found():
    response = client.delete("/admin/items/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": ITEM_NOT_FOUND.format(item_id=999)}


def test_non_admin_is_forbidden(monkeypatch, test_item):
    # monkeypatch restores the original override after the test.
    monkeypatch.setitem(
        app.dependency_overrides,
        get_current_user,
        lambda: Users(id=2, username="regular", role=ROLE_USER),
    )
    response = client.get("/admin/items")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": INSUFFICIENT_PERMISSIONS}
    assert client.delete(f"/admin/items/{test_item.id}").status_code == status.HTTP_403_FORBIDDEN
