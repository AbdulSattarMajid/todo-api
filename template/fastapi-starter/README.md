# My API

FastAPI starter: JWT auth, users, an example `items` feature, SQLAlchemy + Alembic, pytest, Docker.
Runs on **MySQL** or **SQL Server** (and SQLite for quick experiments) by changing `DATABASE_URL` only.

Full step-by-step setup and the "add a new feature" recipe: see `docs/NEW_PROJECT_GUIDE.md` in the
TodoApp reference repo this template came from.

## Quick start (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt -c requirements.lock.txt

Copy-Item .env.example .env        # then set DATABASE_URL and SECRET_KEY
alembic upgrade head               # create / update tables
uvicorn app.main:app --reload      # http://127.0.0.1:8000/docs
pytest                             # tests use SQLite, never your real DB
```

## With Docker

```powershell
docker compose -f docker-compose.mysql.yml up --build    # API + MySQL 8.4
docker compose -f docker-compose.mssql.yml up --build    # API + SQL Server 2022
```

## Endpoints

| Method | Path | Auth |
|---|---|---|
| GET | `/health` | — |
| POST | `/auth/user` (sign up) · `/auth/token` (log in) | — |
| GET | `/user/me` · PUT `/user/change-password` | User |
| GET/POST | `/items` · GET/PUT/DELETE `/items/{id}` | User (own items only) |
| GET | `/admin/items` · DELETE `/admin/items/{id}` | Admin |
