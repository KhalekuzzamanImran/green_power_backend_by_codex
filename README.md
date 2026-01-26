# Green Power Backend

Backend services for telemetry ingestion, aggregation, and API access.

## Tech Stack
- Django 5 + DRF
- MongoDB for telemetry data
- PostgreSQL for relational data
- Redis for cache/queues
- Celery + Beat for aggregations
- Channels for realtime
- Docker Compose for local stack

## Services
- **backend**: Django API
- **mqtt**: MQTT subscriber
- **tcp**: TCP listener
- **celery_worker**: background tasks
- **celery_beat**: scheduled tasks
- **green_power_mongodb**: MongoDB
- **green_power_postgres**: PostgreSQL
- **green_power_redis**: Redis

## Environment
Create a `.env` in the project root with required values, e.g.:
```
DEBUG=0
SECRET_KEY=your-secret
ALLOWED_HOSTS=*
ENVIRONMENT=prod

POSTGRES_DB_NAME=green_power
POSTGRES_DB_USER=green_power_user
POSTGRES_DB_PASSWORD=green_power_pwd
POSTGRES_DB_HOST=green_power_postgres
POSTGRES_DB_PORT=5432

MONGO_DB_URI=mongodb://green_power_user:green_power_pwd@green_power_mongodb:27017/green_power?authSource=admin
MONGO_DB_USER=green_power_user
MONGO_DB_PASSWORD=green_power_pwd
MONGO_DB_NAME=green_power

REDIS_HOST=green_power_redis
REDIS_URL=redis://green_power_redis:6379/0

JWT_SIGNING_KEY=change-me
```

Optional TTL overrides:
```
MONGO_TODAY_TTL_SECONDS=86400
MONGO_LAST_7_DAYS_TTL_SECONDS=604800
MONGO_LAST_30_DAYS_TTL_SECONDS=2592000
MONGO_LAST_6_MONTHS_TTL_SECONDS=15552000
MONGO_THIS_YEAR_TTL_SECONDS=31536000
```

## Run with Docker
From the project root:
```
docker compose -f docker/docker-compose.yml --env-file ./.env up --build
```

Restart services when code or schedules change:
```
docker compose -f docker/docker-compose.yml --env-file ./.env restart backend celery_worker celery_beat mqtt tcp
```

## API Docs
- Swagger: `/api/docs/`
- Schema: `/api/schema/`

## Key API Endpoints
- Health: `/api/health/`, `/api/ready/`
- Auth: `/api/users/token/`, `/api/users/token/refresh/`, `/api/users/token/logout/`
- RT data: `/api/telemetry/rt-data/`
- ENY NOW data: `/api/telemetry/eny-now-data/`
- Environment data: `/api/telemetry/environment-data/`
- Solar data: `/api/telemetry/solar-data/`
- Generator data: `/api/telemetry/generator-data/`
- Telemetry events (Mongo): `/api/telemetry/events/`

### RT Data / ENY NOW Query
Query params:
- `start_time` (ISO 8601)
- `end_time` (ISO 8601)
- `device_id` (optional)
- `page`, `page_size`

Example:
```
/api/telemetry/rt-data/?start_time=2026-01-26T00:00:00Z&end_time=2026-01-26T12:00:00Z&page=1&page_size=50
```

## Aggregations (Celery)
- RT data aggregated by 1m, 10m, 30m, 3h, 6h
- ENY NOW data aggregated by 30m, 3h, 6h
- Environment data aggregated by 1m, 10m, 30m, 3h, 6h

## Telemetry Collections (Mongo)
- `grid_rt_data`, `today_grid_rt_data`, `last_7_days_grid_rt_data`, `last_30_days_grid_rt_data`, `last_6_months_grid_rt_data`, `this_year_grid_rt_data`
- `grid_eny_now_data`, `today_grid_eny_now_data`, `last_7_days_grid_eny_now_data`, `last_30_days_grid_eny_now_data`, `last_6_months_grid_eny_now_data`, `this_year_grid_eny_now_data`
- `environment_data`, `today_environment_data`, `last_7_days_environment_data`, `last_30_days_environment_data`, `last_6_months_environment_data`, `this_year_environment_data`
- `telemetry_events`

## Postman
Import `green_power_backend.postman_collection.json` from the project root.

## Indexes
Run once during deployment:
```
python manage.py ensure_mongo_indexes
```
- Telemetry timestamps are stored as BSON dates for range queries.
