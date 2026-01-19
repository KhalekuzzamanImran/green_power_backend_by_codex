# Selectors

Selectors are read-only and return DTOs only. They must never return ORM instances
and must never perform ORM writes. Use primary-read selectors for write-adjacent
reads to avoid replica lag.

See `ARCHITECTURE.md` and `ENGINEERING_RULES.md` for full contract details.
