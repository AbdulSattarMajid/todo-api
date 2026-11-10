"""Application entry point: `uvicorn app.main:app --reload`.

The schema is managed by Alembic (`python -m scripts.migrate`), not created here.
"""
from fastapi import FastAPI, status

from app.core.config import settings
from app.core.constants import HEALTH_PATH, HEALTH_TAG, HEALTHY_STATUS
from app.routers import admin, auth, todos, users

app = FastAPI(title=settings.APP_NAME)

import os
if os.getenv("AIOPS_API_URL") and os.getenv("AIOPS_API_KEY"):
    from aiops_sdk import install
    install(app, api_url=os.environ["AIOPS_API_URL"],
            api_key=os.environ["AIOPS_API_KEY"],
            service_name="todo-api")


@app.get(HEALTH_PATH, status_code=status.HTTP_200_OK, tags=[HEALTH_TAG])
def health_check():
    return {"status": HEALTHY_STATUS}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
