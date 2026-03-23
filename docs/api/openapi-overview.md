# Green Power EMS Backend API

Base URL: `/api/v1/`

Authentication:
- JWT Bearer tokens
- Obtain tokens from `POST /api/v1/auth/login/`
- Refresh tokens from `POST /api/v1/auth/refresh/`
- Bootstrap current user from `GET /api/v1/auth/me/`

Primary role model:
- `ADMIN`: manage users, assignments, clients, devices, dashboards, thresholds, and audit visibility
- `OM`: read assigned clients/devices/data, view dashboards, update thresholds on accessible devices
- `CLIENT`: read only their client scope and assigned dashboards

Core endpoints:
- `GET|POST|PATCH|DELETE /api/v1/users/`
- `GET|POST|PATCH|DELETE /api/v1/clients/`
- `GET /api/v1/clients/my/`
- `GET|POST|PATCH|DELETE /api/v1/devices/`
- `GET /api/v1/devices/{id}/topics/`
- `GET|POST|PATCH|DELETE /api/v1/topics/`
- `GET /api/v1/topics/{id}/data/`
- `GET /api/v1/topics/{id}/data/latest/`
- `GET|POST /api/v1/topic-data/`
  Supports filters: `?topic_code=mqtt_rt_data`, `?topic_id=...`, `?device_id=...`
- `GET /api/v1/client-types/`
- `GET /api/v1/dashboard-scopes/`
- `GET /api/v1/dashboards/`
  Supports filters: `?client_type=GRID_TIED&scope=MANAGEMENT`
- `GET /api/v1/dashboards/my/`
- `GET|POST|PATCH|DELETE /api/v1/assignments/om-client/`
- `GET|POST|PATCH|DELETE /api/v1/user-client-accesses/`
- `GET|POST|PATCH|DELETE /api/v1/permission-overrides/`
- `GET|POST|PATCH|DELETE /api/v1/thresholds/`
- `GET /api/v1/audit-logs/`

Management commands:
- `python manage.py bootstrap_superuser --username admin --email admin@example.com --password strongpass`
- `python manage.py seed_master_dashboards`
- `python manage.py seed_integration_data --password ChangeMe123!`

Seeded integration users:
- `admin_demo`
- `om_demo`
- `client_grid_management`
- `client_industry_board`

Docs routes:
- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/docs/swagger/`
- Redoc UI: `/api/docs/redoc/`
