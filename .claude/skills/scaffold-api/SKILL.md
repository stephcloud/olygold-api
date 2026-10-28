---
name: scaffold-api
description: Create the initial FastAPI project skeleton (folders, config, DB session, health endpoint, Alembic, pytest setup). Use once at the start of a new project.
disable-model-invocation: true
---

# Scaffold API

1. Read `CLAUDE.md` for the project name, stack, hard rules, and folder structure.
2. Create the folder structure described there, with `__init__.py` files.
3. Create:
   - `app/main.py` with app creation, CORS from `CORS_ORIGINS`, and a `GET /health` endpoint
   - `app/core/config.py` using pydantic-settings (all variables from `.env.example`)
   - `app/db/session.py` (async engine, session dependency) and `app/db/base.py`
   - `requirements.txt` (or `pyproject.toml`), `pytest.ini`
   - `app/tests/conftest.py` with an async test client fixture and a health test
4. Initialize Alembic (async template) and wire it to `app.db.base` metadata and `DATABASE_URL`.
5. Do not create models, auth, or any business endpoints. Those are separate phases.
6. Run `pytest` and report the result. List which dependencies were added.
