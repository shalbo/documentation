# Rousto API

FastAPI REST backend for the Rousto Auto Care platform.

Specification: [`../../docs/02_BACKEND_APIS.md`](../../docs/02_BACKEND_APIS.md)

## Run with Docker (recommended)

```bash
cd rousto/backend
docker compose up -d
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

## Run locally

```bash
cd rousto/backend/api
pip install -r requirements.txt
export DATABASE_URL=postgresql://rousto:rousto_dev@localhost:5432/rousto
uvicorn app.main:app --reload --port 8000
```

## Auth (dev)

```
X-User-Id: a0000000-0000-4000-8000-000000000001
```

## Examples

```bash
# Public catalog
curl http://localhost:8000/api/v1/services

# Profile
curl -H "X-User-Id: a0000000-0000-4000-8000-000000000001" \
  http://localhost:8000/api/v1/me

# Active booking + tracking
curl -H "X-User-Id: a0000000-0000-4000-8000-000000000001" \
  http://localhost:8000/api/v1/bookings/active

curl -H "X-User-Id: a0000000-0000-4000-8000-000000000001" \
  http://localhost:8000/api/v1/bookings/i0000000-0000-4000-8000-000000000001/tracking
```

## Tests

```bash
pip install -r requirements.txt
pytest tests/ -q

# With live database:
ROUSTO_TEST_DB=1 DATABASE_URL=postgresql://rousto:rousto_dev@localhost:5432/rousto \
  pytest tests/ -q
```
