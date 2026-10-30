from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import PASSWORD_MIN_LENGTH


class UserResponse(BaseModel):
    """Public view of a user — deliberately excludes hashed_password."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=PASSWORD_MIN_LENGTH)


class MessageResponse(BaseModel):
    message: str
