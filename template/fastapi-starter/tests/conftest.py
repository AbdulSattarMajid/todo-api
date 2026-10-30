import os

# Settings are read when the app is imported, so point them at the test database first.
# Forcing DATABASE_URL guarantees tests can never touch the real database from .env.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest  # noqa: E402 - must come after the environment is configured
from sqlalchemy import text  # noqa: E402

from app.core.constants import ROLE_ADMIN  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.models import Items, Users  # noqa: E402
from app.dependencies import get_current_user, get_db  # noqa: E402
from app.main import app  # noqa: E402

from .utils import (  # noqa: E402
    TEST_USER_ID,
    TEST_USER_PASSWORD,
    TestingSessionLocal,
    engine,
    override_get_current_user,
    override_get_db,
)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def clear_tables():
    # Children before parents, so foreign keys are never violated.
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM items"))
        connection.execute(text("DELETE FROM users"))
        connection.commit()


@pytest.fixture(autouse=True)
def test_user():
    clear_tables()  # Remove leftovers from interrupted earlier runs
    user = Users(
        id=TEST_USER_ID,
        username="testuser",
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        hashed_password=hash_password(TEST_USER_PASSWORD),
        role=ROLE_ADMIN,
        is_active=True,
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    yield user
    clear_tables()


@pytest.fixture
def test_item(test_user):
    item = Items(name="Test Item", description="This is a test item", owner_id=test_user.id)
    db = TestingSessionLocal()
    db.add(item)
    db.commit()
    db.refresh(item)
    db.close()
    yield item
