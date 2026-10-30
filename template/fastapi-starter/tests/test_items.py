from fastapi import status

from app.core.constants import ITEM_NOT_FOUND
from app.db.models import Items

from .utils import client, TestingSessionLocal, TEST_USER_ID


def item_to_dict(item):
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "owner_id": item.owner_id,
    }


def get_item_from_db(item_id):
    db = TestingSessionLocal()
    try:
        return db.query(Items).filter(Items.id == item_id).first()
    finally:
        db.close()


def test_read_all_authenticated(test_item):
    response = client.get("/items")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [item_to_dict(test_item)]


def test_read_one_authenticated(test_item):
    response = client.get(f"/items/{test_item.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == item_to_dict(test_item)


def test_read_one_not_found():
    response = client.get("/items/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": ITEM_NOT_FOUND.format(item_id=999)}


def test_create_item():
    new_item = {"name": "New Item", "description": "Created in a test"}
    response = client.post("/items", json=new_item)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == new_item["name"]
    assert data["description"] == new_item["description"]
    assert data["owner_id"] == TEST_USER_ID
    assert get_item_from_db(data["id"]) is not None


def test_create_item_without_description():
    response = client.post("/items", json={"name": "No description"})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["description"] is None


def test_create_item_invalid_payload():
    response = client.post("/items", json={"name": "No"})  # too short (min 3)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_item(test_item):
    updated = {"name": "Updated Item", "description": "Updated in a test"}
    response = client.put(f"/items/{test_item.id}", json=updated)
    assert response.status_code == status.HTTP_200_OK
    model_item = get_item_from_db(test_item.id)
    assert model_item.name == updated["name"]
    assert model_item.description == updated["description"]


def test_update_item_not_found():
    response = client.put("/items/999", json={"name": "Updated Item"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_item(test_item):
    response = client.delete(f"/items/{test_item.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert get_item_from_db(test_item.id) is None


def test_delete_item_not_found():
    response = client.delete("/items/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
