# قاعدة بيانات روستو

PostgreSQL schema for the Rousto Auto Care platform.

Full specification: [`../docs/01_DATABASE_SCHEMA.md`](../docs/01_DATABASE_SCHEMA.md)

## Quick start (Docker)

```bash
cd rousto/backend
docker compose up -d
```

On first start, PostgreSQL automatically runs:

1. `001_schema.sql` — tables, enums, indexes, triggers
2. `002_seed.sql` — demo data (سعود العتيبي, active booking, services…)

## Verify

```bash
docker compose exec db psql -U rousto -d rousto -c "\dt"
docker compose exec db psql -U rousto -d rousto -c "SELECT reference, status FROM bookings;"
```

## Connection string

```
postgresql://rousto:rousto_dev@localhost:5432/rousto
```

## API

After `docker compose up -d`, the REST API is available at http://localhost:8000/docs.
See [`../api/README.md`](../api/README.md).

## Reset

```bash
docker compose down -v
docker compose up -d
```

## Manual apply (without Docker)

```bash
psql -U rousto -d rousto -f 001_schema.sql
psql -U rousto -d rousto -f 002_seed.sql
```
