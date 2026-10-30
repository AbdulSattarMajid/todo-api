# ---- Base image: small official Python image, pinned to Debian 12 (bookworm) ----
# Pinned so the Microsoft ODBC apt repository below always matches the OS release.
FROM python:3.13-slim-bookworm

# Set to 0 for MySQL-only images to skip the SQL Server ODBC driver (~20 MB smaller).
ARG INSTALL_MSSQL_ODBC=1

# Don't write .pyc files; flush logs straight to the console
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# pyodbc needs Microsoft's "ODBC Driver 18 for SQL Server" installed in the OS.
# libgssapi-krb5-2 is only "recommended" by msodbcsql18, but the driver won't load without it.
RUN if [ "$INSTALL_MSSQL_ODBC" = "1" ]; then \
        apt-get update \
        && apt-get install -y --no-install-recommends curl gnupg ca-certificates \
        && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
        && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list -o /etc/apt/sources.list.d/mssql-release.list \
        && apt-get update \
        && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 unixodbc libgssapi-krb5-2 \
        && apt-get purge -y curl gnupg && apt-get autoremove -y \
        && rm -rf /var/lib/apt/lists/*; \
    fi

WORKDIR /code

# Install dependencies first so this layer is cached until requirements change.
# -c applies the lock file as constraints: every package (incl. transitive) gets its locked version.
COPY requirements.txt requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.txt -c requirements.lock.txt

# Copy the application code
COPY . .

# Run as a non-root user
RUN useradd --create-home appuser && chown -R appuser /code
USER appuser

EXPOSE 8000

# Migrate the schema, then start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
