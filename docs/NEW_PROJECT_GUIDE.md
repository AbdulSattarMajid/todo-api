# Starting a New FastAPI Project from This Template

A step-by-step guide to creating a new API with the same structure as TodoApp, on **MySQL** or **Microsoft SQL Server (MSSQL)**, with exact dependency versions.

Follow the steps in order the first time. After that, use the [checklist](#13-new-project-checklist) at the end.

> **Concepts** (dependency injection, JWT, migrations, testing) are explained in the main [README](../README.md). This guide covers the **how**, and links there for the **why**.

---

## Contents

0. [What you get](#0-what-you-get)
1. [Prerequisites](#1-prerequisites)
2. [Create the project from the template](#2-create-the-project-from-the-template)
3. [Virtual environment and exact dependencies](#3-virtual-environment-and-exact-dependencies)
4. [Configure `.env`](#4-configure-env)
5. [Database setup — MySQL and SQL Server](#5-database-setup--mysql-and-sql-server)
6. [Migrations](#6-migrations)
7. [Run and try the API](#7-run-and-try-the-api)
8. [Add a new feature (the repeatable recipe)](#8-add-a-new-feature-the-repeatable-recipe)
9. [Testing](#9-testing)
10. [Docker](#10-docker)
11. [Keeping versions under control](#11-keeping-versions-under-control)
12. [Troubleshooting](#12-troubleshooting)
13. [New-project checklist](#13-new-project-checklist)

---

## 0. What you get

The template lives in [`template/fastapi-starter/`](../template/fastapi-starter/). It is TodoApp with the Todo-specific parts replaced by a neutral example feature called **items**.

```
my-api/
├── app/
│   ├── main.py              # Creates the app, /health, registers routers
│   ├── dependencies.py      # get_db, get_current_user, get_current_admin
│   ├── core/
│   │   ├── config.py        # Settings from .env (pydantic-settings)
│   │   ├── constants.py     # Prefixes, roles, column sizes, messages
│   │   └── security.py      # bcrypt hashing + JWT
│   ├── db/
│   │   ├── database.py      # engine, SessionLocal, Base (MySQL / MSSQL / SQLite)
│   │   └── models.py        # Users + Items
│   ├── schemas/             # Pydantic request/response models
│   └── routers/             # auth.py, users.py, items.py, admin.py
├── alembic/versions/0001_initial.py   # Creates users + items
├── tests/                   # 32 tests, run against SQLite
├── .env.example             # MySQL and MSSQL URL examples
├── requirements.txt         # Exact versions you chose
├── requirements-dev.txt     # + pytest, httpx
├── requirements.lock.txt    # Exact versions of EVERY package (incl. transitive)
├── Dockerfile               # Includes the SQL Server ODBC driver
├── docker-compose.mysql.yml # API + MySQL 8.4
└── docker-compose.mssql.yml # API + SQL Server 2022
```

**What each layer does** (same as TodoApp — see [README §3](../README.md#3-project-structure)):

| Layer | Job | Should not |
|---|---|---|
| `routers/` | HTTP: paths, status codes, calling the DB | Hold config or reusable security logic |
| `schemas/` | Shape and validation of API input/output | Know about the database |
| `db/models.py` | Shape of database tables | Know about HTTP |
| `dependencies.py` | Build shared objects per request | Contain one route's business rules |
| `core/` | Config, constants, security helpers | Import from routers |

**Differences from TodoApp:**

- No `scripts/migrate.py`. TodoApp needed it because Alembic was added after the tables existed. A new project starts with Alembic from migration `0001`, so `alembic upgrade head` is all you need.
- Every `String` column has an explicit length, taken from `constants.py`. MySQL requires a length, and SQL Server can't index `VARCHAR(max)`.
- `database.py` turns on `fast_executemany` automatically for SQL Server.
- Every dependency version is pinned.

---

## 1. Prerequisites

Install these once per machine.

| Tool | Version | Why | Check |
|---|---|---|---|
| Python | **3.13.x** | Runs the app | `python --version` |
| Git | any recent | Version control | `git --version` |
| Docker Desktop | any recent | Run MySQL / SQL Server without installing them, and build the API image | `docker --version` |
| VS Code + Python extension | any | Editor | — |

**For SQL Server (MSSQL)** — also needed even if SQL Server itself runs in Docker, because your local Python talks to it through ODBC:

| Tool | Why | Check (PowerShell) |
|---|---|---|
| **Microsoft ODBC Driver 18 for SQL Server** (x64) | `pyodbc` cannot connect without it | `Get-OdbcDriver -Platform 64-bit \| Where Name -like "*SQL Server*"` → must list `ODBC Driver 18 for SQL Server` |
| SQL Server 2022 Developer or Express *(optional)* | Only if you want a local install instead of Docker | — |
| SSMS or Azure Data Studio *(optional)* | GUI to browse the database | — |

Download the ODBC driver from Microsoft's "Download ODBC Driver for SQL Server" page.

**For MySQL** *(optional — Docker works too)*: MySQL Server 8.4 and MySQL Workbench.

---

## 2. Create the project from the template

```powershell
# 1. Copy the template to a new folder (outside the TodoApp repo)
Copy-Item -Recurse C:\Users\veeru\ihl\pp\fastapi\TodoApp\template\fastapi-starter C:\Users\veeru\projects\inventory-api
cd C:\Users\veeru\projects\inventory-api

# 2. Start a fresh git history
git init
git add .
git commit -m "Initial commit from fastapi-starter template"
```

Then give it your project's name:

| Where | Change |
|---|---|
| `.env` (step 4) | `APP_NAME=Inventory API` |
| `app/core/config.py` | Default `APP_NAME` (used if `.env` doesn't set it) |
| `README.md` | Title and description |
| `.env.example` | Database name `appdb` → e.g. `inventorydb` (in every URL and in `MYSQL_DATABASE` / `MSSQL_DATABASE`) |

---

## 3. Virtual environment and exact dependencies

A virtual environment keeps this project's packages separate from every other project on your machine.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1          # your prompt now starts with (.venv)
python -m pip install --upgrade pip
pip install -r requirements-dev.txt -c requirements.lock.txt
pip check                           # must print: No broken requirements found.
```

> If PowerShell refuses to run `Activate.ps1`, run this once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
> On macOS/Linux use `source .venv/bin/activate`.

**What the three requirement files are for:**

| File | Contains | Used by |
|---|---|---|
| `requirements.txt` | The packages **you chose**, each with an exact `==` version | Docker image, production |
| `requirements-dev.txt` | `-r requirements.txt` + `pytest` + `httpx` | Your laptop, CI |
| `requirements.lock.txt` | **Every** package, including the ones pulled in indirectly (`starlette`, `anyio`, `greenlet`…) | Passed with `-c` as a *constraints* file |

`-c requirements.lock.txt` means "whatever gets installed must be exactly this version". It doesn't add packages, it only pins them. That's why the same lock file works on Windows and in the Linux Docker image, even though each OS needs a slightly different set of packages.

### The exact versions

Verified together: `pip check` is clean, all 32 tests pass, and both Docker stacks work end to end.

| Package | Version | Purpose |
|---|---|---|
| fastapi | 0.115.5 | Web framework |
| starlette | 0.41.3 | ASGI toolkit under FastAPI (0.115.5 requires < 0.42) |
| uvicorn[standard] | 0.32.1 | ASGI server |
| gunicorn | 26.2.0 | Process manager for production workers |
| python-multipart | 0.0.32 | Form parsing for the `/auth/token` login |
| pydantic | 2.10.3 | Validation |
| pydantic-settings | 2.16.1 | Settings from `.env` |
| email-validator | 2.3.0 | `EmailStr` |
| SQLAlchemy | 2.0.41 | ORM |
| alembic | 1.16.4 | Migrations |
| **PyMySQL** | **1.1.1** | **MySQL driver** (`mysql+pymysql://`) |
| **cryptography** | **45.0.5** | **MySQL 8 authentication** (`caching_sha2_password`) |
| **pyodbc** | **5.2.0** | **SQL Server driver** (`mssql+pyodbc://`) |
| passlib | 1.7.4 | Password hashing API |
| bcrypt | **4.0.1** | Hash backend. **Keep at 4.0.1**: newer bcrypt breaks passlib |
| python-jose[cryptography] | 3.5.0 | JWT encode/decode |
| pytest *(dev)* | 9.1.1 | Tests |
| httpx *(dev)* | 0.28.1 | Used by `TestClient` |

Transitive versions (anyio 4.15.1, greenlet 3.5.6, h11 0.16.0, …) are in `requirements.lock.txt`.

---

## 4. Configure `.env`

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"    # paste the output into SECRET_KEY
```

Open `.env` and set:

```ini
APP_NAME=Inventory API
DATABASE_URL=<pick one from section 5>
SECRET_KEY=<the 64-character value you just generated>
ACCESS_TOKEN_EXPIRE_MINUTES=20
```

- `.env` is gitignored. **Never commit it.** Commit only `.env.example`, with placeholder values.
- The app refuses to start if `DATABASE_URL` or `SECRET_KEY` is missing. That's intentional (see [README §8](../README.md#8-configuration-env-and-constants)).
- Real environment variables override `.env`. Docker Compose uses this to point the API at the database container.

---

## 5. Database setup — MySQL and SQL Server

The code is identical for both databases. Only `DATABASE_URL` changes:

```
dialect+driver://username:password@host:port/database?options
```

**Passwords with special characters** must be URL-encoded in the URL: `@` → `%40`, `#` → `%23`, `/` → `%2F`, `:` → `%3A`, `%` → `%25`. `!` is fine as-is. To encode one:

```powershell
python -c "from urllib.parse import quote_plus; print(quote_plus('p@ss#word'))"
```

Pick **5a** or **5b**.

### 5a. MySQL

#### Option 1 — MySQL in Docker (no install)

```powershell
docker compose -f docker-compose.mysql.yml up -d db      # creates the database automatically
```

```ini
DATABASE_URL=mysql+pymysql://root:root@localhost:3307/appdb?charset=utf8mb4
```

Port **3307** on your machine maps to 3306 in the container, so it won't clash with a locally installed MySQL.

#### Option 2 — Locally installed MySQL 8.x

Create the database once (MySQL Workbench or the `mysql` client):

```sql
CREATE DATABASE appdb CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- Recommended: a dedicated user instead of root
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'Str0ngPass!';
GRANT ALL PRIVILEGES ON appdb.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
```

```ini
DATABASE_URL=mysql+pymysql://appuser:Str0ngPass!@localhost:3306/appdb?charset=utf8mb4
```

**Why `?charset=utf8mb4`:** MySQL's old `utf8` can't store emoji and some other characters. `utf8mb4` is full UTF-8.

### 5b. Microsoft SQL Server (MSSQL)

First confirm the ODBC driver is installed (see [Prerequisites](#1-prerequisites)). The `driver=` value in the URL must match the installed driver name **exactly**, with spaces written as `+`.

#### Option 1 — SQL Server in Docker (no install)

```powershell
docker compose -f docker-compose.mssql.yml up -d db db-init
```

- `db` starts SQL Server 2022 (Developer edition, free for development).
- `db-init` waits until SQL Server is healthy, runs `CREATE DATABASE appdb` if it doesn't exist, then exits. SQL Server has no built-in "create a database on first start" setting, unlike MySQL.

```ini
DATABASE_URL=mssql+pyodbc://sa:YourStr0ng!Passw0rd@localhost:1434/appdb?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

Port **1434** on your machine maps to 1433 in the container, so it won't clash with a local SQL Server.

#### Option 2 — Locally installed SQL Server, SQL login

1. During installation choose **Mixed Mode** authentication and set an `sa` password (or create a login later).
2. **Express only:** TCP/IP is off by default. Open *SQL Server Configuration Manager* → *SQL Server Network Configuration* → *Protocols for SQLEXPRESS* → enable **TCP/IP**, then restart the SQL Server service.
3. Create the database and a login (SSMS → New Query):

```sql
CREATE DATABASE appdb;
GO
CREATE LOGIN appuser WITH PASSWORD = 'Str0ngPass!';
GO
USE appdb;
CREATE USER appuser FOR LOGIN appuser;
ALTER ROLE db_owner ADD MEMBER appuser;   -- needed so Alembic can create tables
GO
```

```ini
# Default instance on port 1433
DATABASE_URL=mssql+pyodbc://appuser:Str0ngPass!@localhost:1433/appdb?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

#### Option 3 — Locally installed SQL Server, Windows authentication

No username or password in the URL. Your Windows account must have access to the database.

```ini
# Named instance (e.g. SQLEXPRESS) — requires the "SQL Server Browser" service to be running
DATABASE_URL=mssql+pyodbc://@localhost\SQLEXPRESS/appdb?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes

# Default instance
DATABASE_URL=mssql+pyodbc://@localhost/appdb?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes
```

Windows authentication only works when the app runs on Windows. Inside Docker (Linux), use a SQL login.

#### What the URL options mean

| Option | Meaning |
|---|---|
| `driver=ODBC+Driver+18+for+SQL+Server` | Which installed ODBC driver to use |
| `TrustServerCertificate=yes` | Driver 18 **encrypts by default** and rejects SQL Server's self-signed certificate. This accepts it. Fine locally; in production use a real certificate and drop this option |
| `trusted_connection=yes` | Use Windows authentication instead of a username/password |

#### SQL Server things to know

| Topic | What happens | What to do |
|---|---|---|
| `Boolean` columns | Stored as `BIT` (0/1) | Nothing. SQLAlchemy converts to `True`/`False` |
| `String` without a length | Becomes `VARCHAR(max)`, which **can't be indexed or made unique** | Always give a length (the template does) |
| Unique + nullable column | SQL Server allows only **one** `NULL` in a unique column (MySQL allows many) | Make unique columns `nullable=False`, or use a filtered index |
| `sa` password | Rejected if weak: needs 8+ chars and 3 of upper, lower, digit, symbol | Container exits immediately if the password is too weak — check `docker compose logs db` |
| Reserved words | `user`, `order`, `key`… are reserved | Use plural table names (`users`, `orders`) like the template |

### Test the connection before going further

```powershell
python -c "from sqlalchemy import text; from app.db.database import engine; c = engine.connect(); print(c.execute(text('SELECT 1')).scalar()); c.close()"
```

It prints `1` on success. Otherwise see [Troubleshooting](#12-troubleshooting).

---

## 6. Migrations

### First run: create the tables

```powershell
alembic upgrade head          # runs 0001_initial → creates users, items, alembic_version
alembic current               # prints: 0001 (head)
```

### Every schema change afterwards

```powershell
# 1. Edit app/db/models.py (add a column, a table, ...)
# 2. Generate a migration by comparing models to the database
alembic revision --autogenerate -m "add sku to items"
# 3. READ the generated file in alembic/versions/ — fix it if needed
# 4. Apply it
alembic upgrade head
# 5. Commit models.py and the migration file together
```

Other commands: `alembic downgrade -1` (undo the last one), `alembic history`, `alembic check` (fails if models and migrations don't match — useful in CI).

### Rules that keep migrations safe

- **Always review autogenerated files.** Alembic sees a column *rename* as drop + add, which loses the data. Replace it with `op.alter_column("items", "old", new_column_name="new")`.
- **Adding a `NOT NULL` column to a table that already has rows** fails unless you give a `server_default`:
  ```python
  op.add_column("items", sa.Column("sku", sa.String(50), nullable=False, server_default=""))
  ```
- **Never edit a migration that has already run** on a shared database. Create a new one.
- On **SQL Server**, dropping a column that has a default or an index fails until the constraint or index is dropped first. Autogenerate doesn't always handle this, which is another reason to read the file.
- Run migrations on **both** databases if a project supports both. A migration that works on MySQL can fail on SQL Server.

More background: [README §11](../README.md#11-database-migrations-with-alembic).

---

## 7. Run and try the API

```powershell
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs**:

1. `POST /auth/user` → create a user.
2. Click **Authorize** (top right) → log in with that username and password.
3. Call `POST /items`, then `GET /items`.
4. `GET /user/me` shows your profile, without the password hash.

To get an **admin** user, sign up with `"role": "admin"` in the body. For a real project, remove that ability: drop `role` from `CreateUserRequest` in `app/schemas/auth.py` and promote admins directly in the database.

---

## 8. Add a new feature (the repeatable recipe)

Every new resource follows the same seven steps. Worked example: a **products** feature.

### Step 1 — Constants (`app/core/constants.py`)

```python
PRODUCTS_PREFIX = "/products"
PRODUCTS_TAG = "products"

PRODUCT_NAME_MIN_LENGTH = 2
PRODUCT_NAME_MAX_LENGTH = 150
PRODUCT_SKU_MAX_LENGTH = 50

PRODUCT_NOT_FOUND = "Product with id {product_id} not found"
```

### Step 2 — Model (`app/db/models.py`)

```python
from sqlalchemy import Numeric

class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(PRODUCT_NAME_MAX_LENGTH), nullable=False)
    sku = Column(String(PRODUCT_SKU_MAX_LENGTH), unique=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)      # exact decimal; never Float for money
    in_stock = Column(Boolean, default=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
```

### Step 3 — Migration

```powershell
alembic revision --autogenerate -m "create products table"
# review alembic/versions/xxxx_create_products_table.py
alembic upgrade head
```

### Step 4 — Schemas (`app/schemas/product.py`)

```python
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import PRODUCT_NAME_MAX_LENGTH, PRODUCT_NAME_MIN_LENGTH, PRODUCT_SKU_MAX_LENGTH


class ProductRequest(BaseModel):
    name: str = Field(min_length=PRODUCT_NAME_MIN_LENGTH, max_length=PRODUCT_NAME_MAX_LENGTH)
    sku: str = Field(min_length=1, max_length=PRODUCT_SKU_MAX_LENGTH)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    in_stock: bool = True


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    price: Decimal
    in_stock: bool
    owner_id: int
```

### Step 5 — Router (`app/routers/products.py`)

Copy `app/routers/items.py` and rename `Items` → `Products`, `item` → `product`, the constants and the schemas. The structure stays the same:

- `get_owned_product_or_404()` helper (returns 404 for other users' products)
- `GET ""`, `POST ""`, `GET /{product_id}`, `PUT /{product_id}`, `DELETE /{product_id}`
- Every route takes `user: CurrentUser, db: DbSession`

> **Find-and-replace trap:** replacing `item` → `product` also changes `item.model_dump().items()` in `update_item` into `.products()`, which crashes at runtime with `'dict' object has no attribute 'products'`. Keep `.items()` — it's Python's `dict.items()`, not the feature name.

### Step 6 — Register it (`app/main.py`)

```python
from app.routers import admin, auth, items, products, users
...
app.include_router(products.router)
```

### Step 7 — Tests

1. In `tests/conftest.py`: add `DELETE FROM products` to `clear_tables()`, **before** `DELETE FROM users` (children before parents), and add a `test_product` fixture like `test_item`.
2. Copy `tests/test_items.py` → `tests/test_products.py` and adapt it.
3. Run `pytest`.

### Removing the example `items` feature

Once you have your own features, delete: `app/routers/items.py`, `app/schemas/item.py`, the `Items` model, the `ITEM_*` constants, its lines in `main.py` and `admin.py`, `tests/test_items.py`, the `test_item` fixture and its `clear_tables()` line. Then run `alembic revision --autogenerate -m "drop items table"`.

If the project has **never been deployed**, you can instead edit `0001_initial.py` directly and recreate your local database.

---

## 9. Testing

```powershell
pytest                 # all tests
pytest -v              # list every test
pytest tests/test_items.py::test_create_item
pytest -k "auth"       # names matching "auth"
```

- Tests always use a **SQLite** file (`test.db`). `tests/conftest.py` forces `DATABASE_URL` before the app is imported, so tests can never touch your MySQL or SQL Server data.
- `get_db` and `get_current_user` are replaced with `app.dependency_overrides`, so most tests skip the login step.
- Each test starts with clean tables.

SQLite catches most bugs. Database-specific problems (lengths, unique NULLs, migration SQL) only show up on the real database. Before a release, run `alembic upgrade head` against MySQL and SQL Server in Docker and smoke-test through `/docs`.

More: [README §14](../README.md#14-testing-with-pytest).

---

## 10. Docker

Both stacks build the same `Dockerfile`. On start, the API container runs `alembic upgrade head`, then starts uvicorn.

```powershell
# MySQL
docker compose -f docker-compose.mysql.yml up --build
# SQL Server
docker compose -f docker-compose.mssql.yml up --build
```

Then open http://localhost:8000/docs.

| Command | What it does |
|---|---|
| `docker compose -f <file> up -d --build` | Start in the background |
| `docker compose -f <file> logs -f api` | Follow API logs |
| `docker compose -f <file> exec api alembic current` | Run a command inside the API container |
| `docker compose -f <file> down` | Stop (data is kept in the volume) |
| `docker compose -f <file> down -v` | Stop **and delete the database** |

**How it fits together:**

- **Dockerfile**: `python:3.13-slim-bookworm`, plus Microsoft's **ODBC Driver 18** (`msodbcsql18`). `pyodbc` needs the driver inside the container too. The MySQL compose file sets `INSTALL_MSSQL_ODBC=0` to skip it.
- Dependencies are installed with `pip install -r requirements.txt -c requirements.lock.txt`, so the image gets exactly the locked versions.
- Inside the compose network the database host is the **service name `db`**, not `localhost`. The compose files override `DATABASE_URL` for the API container.
- **MySQL stack**: `db` (mysql:8.4, healthcheck) → `api`.
- **SQL Server stack**: `db` (sql server 2022, healthcheck) → `db-init` (creates the database, exits) → `api`.
- The container runs as a non-root user.

Want only the database in Docker, with the API running locally for fast reloads? Start the services you need (`up -d db` for MySQL, `up -d db db-init` for SQL Server) and use the `localhost:3307` / `localhost:1434` URLs from section 5.

Deployment checklist and Nginx/HTTPS setup: [README §16](../README.md#16-deployment).

---

## 11. Keeping versions under control

**Rule:** a new project starts from the template's pinned versions. Upgrade on purpose, on a branch, one area at a time — never by accident.

### Upgrading a package

```powershell
git checkout -b chore/upgrade-fastapi

# 1. Change the version in requirements.txt (e.g. fastapi==0.1xx.x)
# 2. Rebuild the lock file from a clean environment
Remove-Item -Recurse -Force .venv
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt          # no -c: let pip pick new transitive versions
pip check
# 3. Regenerate the lock file (keep the 3 comment lines at the top of the old one)
pip freeze > requirements.lock.txt
# 4. Add the dev tools and test
pip install -r requirements-dev.txt -c requirements.lock.txt
pytest
# 5. Smoke-test both Docker stacks (section 10), then commit
```

### Packages to be careful with

| Package | Why |
|---|---|
| **bcrypt** | Must stay **4.0.1** while using `passlib`. Newer versions log `error reading bcrypt version` and reject passwords over 72 bytes |
| **fastapi ↔ starlette** | Each FastAPI release supports only a narrow starlette range. Upgrade them together |
| **pydantic ↔ pydantic_core** | Pinned as a pair. Let pip choose `pydantic_core` |
| **SQLAlchemy** | Stay on 2.0.x. 2.1 may change defaults |
| **pyodbc ↔ ODBC Driver** | `pyodbc` is the Python side; the ODBC Driver 18 install is the OS side. Both must be present |

---

## 12. Troubleshooting

### General

| Problem | Fix |
|---|---|
| `ValidationError: DATABASE_URL / SECRET_KEY Field required` | Create `.env` from `.env.example`, and run commands from the project root |
| `ModuleNotFoundError: No module named 'app'` | Run from the project root (where `alembic.ini` is) |
| `alembic: command not found` / not recognized | Activate the venv, or use `python -m alembic ...` |
| `Target database is not up to date` | `alembic upgrade head` before `alembic revision --autogenerate` |
| `401` in Swagger | Click **Authorize** and log in first |
| `422 Unprocessable Entity` | Read `detail` in the response; it names the invalid field |
| `error reading bcrypt version` | Reinstall with the lock file; bcrypt must be 4.0.1 |

### MySQL

| Problem | Fix |
|---|---|
| `(2003) Can't connect to MySQL server` | Start MySQL, or `docker compose -f docker-compose.mysql.yml up -d db` and use port 3307 |
| `(1049) Unknown database 'appdb'` | `CREATE DATABASE appdb CHARACTER SET utf8mb4;` |
| `(1045) Access denied for user` | Wrong user/password, or the user lacks `GRANT` on the database |
| `'cryptography' package is required` | `pip install -r requirements.txt -c requirements.lock.txt` |
| API container restarts a few times on first start | Normal while MySQL initializes. `restart: on-failure` handles it |

### SQL Server

| Problem | Fix |
|---|---|
| `IM002 Data source name not found and no default driver specified` | ODBC Driver 18 isn't installed, or the `driver=` name in the URL doesn't match. Check with `Get-OdbcDriver` |
| `SSL Provider: certificate verify failed` / `certificate chain was issued by an authority that is not trusted` | Add `&TrustServerCertificate=yes` to the URL (local/dev only) |
| `Login timeout expired` / `TCP Provider: No connection could be made` | SQL Server isn't running, TCP/IP is disabled (Configuration Manager), the port is wrong (Docker = 1434), or the firewall blocks it |
| `Login failed for user 'sa'` | Wrong password, or Mixed Mode authentication is off (local install) |
| SQL Server container exits immediately | `sa` password too weak. Check `docker compose -f docker-compose.mssql.yml logs db` |
| `Cannot open database "appdb" requested by the login` | The database doesn't exist. `CREATE DATABASE appdb;` (Docker: `db-init` does this) |
| Named instance (`localhost\SQLEXPRESS`) not found | Start the **SQL Server Browser** service, or use `localhost:<port>` |
| In Docker: `Can't open lib ... libmsodbcsql-18 ... file not found` | A system library the driver needs is missing. The template's Dockerfile installs `libgssapi-krb5-2`; keep that line if you edit it |
| `Column 'x' in table 'y' is of a type that is invalid for use as a key column in an index` | A `String` without a length became `VARCHAR(max)`. Give it a length |
| `Cannot insert duplicate key ... The duplicate key value is (<NULL>)` | Unique column with more than one NULL. Make it `nullable=False` |

---

## 13. New-project checklist

**Setup**
- [ ] Copy `template/fastapi-starter` to a new folder, `git init`, first commit
- [ ] Rename: `APP_NAME` in `config.py` and `.env.example`, `README.md` title, database name in `.env.example`
- [ ] `python -m venv .venv` → activate → `pip install -r requirements-dev.txt -c requirements.lock.txt` → `pip check`
- [ ] `Copy-Item .env.example .env`, generate `SECRET_KEY`, set `DATABASE_URL`

**Database**
- [ ] MySQL: database created (`utf8mb4`), or `docker compose -f docker-compose.mysql.yml up -d db`
- [ ] SQL Server: ODBC Driver 18 installed, database created, or `docker compose -f docker-compose.mssql.yml up -d db db-init`
- [ ] Connection test prints `1`
- [ ] `alembic upgrade head` → `alembic current` shows `0001 (head)`

**Verify**
- [ ] `pytest` — all green
- [ ] `uvicorn app.main:app --reload` → sign up, authorize, create an item in `/docs`
- [ ] `docker compose -f docker-compose.<db>.yml up --build` works

**Build your features**
- [ ] For each resource: constants → model → migration → schema → router → `main.py` → tests ([section 8](#8-add-a-new-feature-the-repeatable-recipe))
- [ ] Remove the example `items` feature once you have your own
- [ ] Remove `role` from the public sign-up request

**Before production**
- [ ] Real `SECRET_KEY` from a secret store, not from git
- [ ] SQL Server: real TLS certificate, drop `TrustServerCertificate=yes`
- [ ] Dedicated database user (not `root` / `sa`) with only the permissions it needs
- [ ] Migrations run before the new version serves traffic
- [ ] CORS limited to your front-end origins, rate limit on `/auth/token`
- [ ] Production checklist in [README §16](../README.md#16-deployment)
