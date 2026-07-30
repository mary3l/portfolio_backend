# Mabano Portfolio — Backend

FastAPI service backing the portfolio. Reading projects is public; creating,
updating and deleting requires the admin's Supabase access token.

## Getting started

```bash
python -m venv venv
venv/Scripts/activate            # macOS/Linux: source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env             # then fill in your Supabase values
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

Run `supabase_schema.sql` once in the Supabase SQL editor to create the table.

## Endpoints

| Method | Path                 | Auth  |
| ------ | -------------------- | ----- |
| GET    | `/`                  | —     |
| GET    | `/health`            | —     |
| GET    | `/projects/`         | —     |
| GET    | `/projects/{id}`     | —     |
| POST   | `/projects/`         | Admin |
| PATCH  | `/projects/{id}`     | Admin |
| DELETE | `/projects/{id}`     | Admin |

Admin endpoints expect `Authorization: Bearer <supabase access token>`. The
token is verified against Supabase and must belong to `ADMIN_EMAIL`.

`/health` always returns 200 so a probe can tell "app down" (no response) from
"app up, database unreachable" (`{"status": "degraded"}`).

## Structure

```
app/
  main.py               create_app(): CORS, exception handlers, routers
  core/
    config.py           Settings (pydantic-settings) + get_settings()
    security.py         HTTPBearer -> require_admin dependency
    exceptions.py       domain errors -> HTTP responses
  db/supabase.py        client construction and injection
  api/
    router.py           aggregates the route modules
    routes/
      health.py
      projects.py       thin: validate, delegate, return
  schemas/project.py    ProjectCreate / ProjectUpdate / ProjectRead
  services/projects.py  Supabase access, raises domain errors
```

The layering rule: routes handle HTTP, services handle data and raise domain
errors from `core/exceptions.py`, and only `main.py` knows how those map to
status codes. Services never import FastAPI.

## Configuration

| Variable       | Required | Notes                                        |
| -------------- | -------- | -------------------------------------------- |
| `SUPABASE_URL` | yes      | Must be `https://`                           |
| `SUPABASE_KEY` | yes      | `service_role` key; the anon key cannot write |
| `ADMIN_EMAIL`  | yes      | The only account allowed to write            |
| `CORS_ORIGINS` | no       | Comma-separated; defaults to localhost        |
| `DEBUG`        | no       | Defaults to `false`                           |

`ADMIN_EMAIL` is required deliberately: if it were optional, forgetting it would
silently let any signed-in Supabase user modify projects. Invalid configuration
stops the app from starting rather than failing on the first request.

## Lint and format

```bash
ruff check .
ruff format .
```
