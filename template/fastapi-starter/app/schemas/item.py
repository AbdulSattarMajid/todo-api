from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import ITEM_DESCRIPTION_MAX_LENGTH, ITEM_NAME_MAX_LENGTH, ITEM_NAME_MIN_LENGTH


class ItemRequest(BaseModel):
    name: str = Field(min_length=ITEM_NAME_MIN_LENGTH, max_length=ITEM_NAME_MAX_LENGTH)
    description: str | None = Field(default=None, max_length=ITEM_DESCRIPTION_MAX_LENGTH)


class ItemResponse(BaseModel):
    # from_attributes lets Pydantic read values from a SQLAlchemy object.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    owner_id: int
