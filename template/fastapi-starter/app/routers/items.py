from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.core.constants import ITEM_NOT_FOUND, ITEMS_PREFIX, ITEMS_TAG
from app.db.models import Items, Users
from app.dependencies import CurrentUser, DbSession
from app.schemas.item import ItemRequest, ItemResponse

router = APIRouter(prefix=ITEMS_PREFIX, tags=[ITEMS_TAG])


def get_owned_item_or_404(db: Session, item_id: int, user: Users) -> Items:
    """Users can only see their own items; someone else's item looks like a 404."""
    item = db.query(Items).filter(Items.id == item_id, Items.owner_id == user.id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ITEM_NOT_FOUND.format(item_id=item_id))
    return item


@router.get("", response_model=list[ItemResponse], status_code=status.HTTP_200_OK)
def read_all(user: CurrentUser, db: DbSession):
    return db.query(Items).filter(Items.owner_id == user.id).all()


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemRequest, user: CurrentUser, db: DbSession):
    db_item = Items(**item.model_dump(), owner_id=user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=ItemResponse, status_code=status.HTTP_200_OK)
def read_item(user: CurrentUser, db: DbSession, item_id: int = Path(gt=0)):
    return get_owned_item_or_404(db, item_id, user)


@router.put("/{item_id}", response_model=ItemResponse, status_code=status.HTTP_200_OK)
def update_item(item: ItemRequest, user: CurrentUser, db: DbSession, item_id: int = Path(gt=0)):
    db_item = get_owned_item_or_404(db, item_id, user)
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(user: CurrentUser, db: DbSession, item_id: int = Path(gt=0)):
    db_item = get_owned_item_or_404(db, item_id, user)
    db.delete(db_item)
    db.commit()
