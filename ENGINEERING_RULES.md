# Engineering Rules

- No ORM in selectors (read-only DTOs only).
- No replica reads in write paths; use primary reads or IntegrityError handling.
- DTOs are immutable read models; never call ORM methods on selector outputs.
- Use `/api/ready/` for high-frequency probes and `/api/health/` for diagnostics only.
