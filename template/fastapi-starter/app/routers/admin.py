from fastapi import APIRouter, HTTPException, Path, status

from app.core.constants import ADMIN_PREFIX, ADMIN_TAG, ITEM_NOT_FOUND
from app.db.models import Items
from app.dependencies import AdminUser, DbSession
from app.schemas.item import ItemResponse

router = APIRouter(prefix=ADMIN_PREFIX, tags=[ADMIN_TAG])


@router.get("/items", response_model=list[ItemResponse], status_code=status.HTTP_200_OK)
def read_all_items(_admin: AdminUser, db: DbSession):
    return db.query(Items).all()


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(_admin: AdminUser, db: DbSession, item_id: int = Path(gt=0)):
    db_item = db.query(Items).filter(Items.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ITEM_NOT_FOUND.format(item_id=item_id))
    db.delete(db_item)
    db.commit()
