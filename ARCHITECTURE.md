# Architecture

## Layering
- Views: HTTP only (request/response). No business logic.
- Services: Business logic, orchestration, transaction boundaries.
- Selectors: Read models only (DTOs), no ORM writes.
- Repositories: ORM writes only.
- Models: Persistence only.

## Selector Rules
- Selectors return DTOs only (dicts or typed read models).
- Selectors must never return ORM instances.
- ORM writes are forbidden in selectors.
- Use explicit primary-read selectors for write-adjacent reads.

## Read/Write Routing
- Writes always go to the primary database.
- All write-adjacent reads must use the primary DB or rely on IntegrityError handling.
- Replica reads are allowed only for read-safe paths.

## Polyglot Persistence
- User and relational data live in PostgreSQL via Django ORM.
- Time-series data lives in MongoDB via `common/mongo.py` and dedicated repositories.

## Caching Rules
- Cache DTOs only; never cache ORM instances.
- All writes must invalidate related cache keys via centralized invalidation.

## Health Endpoints
- `/api/ready/`: lightweight readiness/liveness (no DB/Redis calls). Safe for high-frequency probes.
- `/api/health/`: deep dependency checks (DB/Redis). Low-frequency manual/LB-only use.

## ASGI Lifespan
- Lifespan must be enabled in production to guarantee Redis cleanup on shutdown.
- Configure Uvicorn/Gunicorn to support lifespan events.

## CI Guard
- `scripts/ci/check_selectors.py` enforces selector contracts:
  - Cached selectors must not return ORM types.
  - Selectors must not use ORM write APIs.
