# Lead Platform

A lead management application for a small sales team — built for Digital Heroes'
Full Stack Development qualification task ("Build a lead platform, not a lead form").

**Live app:** https://lead-platform-iota.vercel.app
**Live API:** https://lead-platform-3pwk.onrender.com/docs

## What this is
- A public, unauthenticated lead-capture form for external visitors
- An authenticated internal app with two roles (admin, member), each with
  enforced permissions on both client and server
- A lead lifecycle: status pipeline, assignment, timestamped notes, and a
  full activity audit trail
- A documented JSON API with pagination, filtering, and proper status codes
- An automated test suite (9 tests) covering auth rules and core flows

## Tech stack
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL (Neon), JWT auth (python-jose, passlib)
- **Frontend:** React + Vite
- **Deployment:** Render (backend), Vercel (frontend), Neon (database) — all free tier

## Data model
Four entities: `User` (admin/member role), `Lead` (the pipeline entity, with
a nullable `assigned_to_id`), `Note` (timestamped, authored by a user), and
`ActivityLog` (system-generated audit trail — separate from Notes because
it captures *every* change, including assignment and status changes, not
just deliberate human comments). See `backend/app/models.py` for the full
schema.

## Key design decisions and tradeoffs
- **JWT in-memory, not localStorage or cookies** — chosen for build speed;
  a page refresh currently logs the user out. The more correct long-term
  approach is an httpOnly cookie set by the server, which JavaScript can't
  read at all, removing the XSS token-theft surface. Not done here due to
  the added session/CSRF-handling complexity within the project timeline.
- **404, not 403, when a member requests a lead they can't see** — avoids
  confirming a lead's existence to someone not permitted to view it.
- **Public capture schema has no `status`/`assigned_to_id` fields at all**
  — the security boundary is enforced by the shape of the Pydantic schema
  itself, not a manual check that could be forgotten.
- **UUID primary keys**, not auto-increment integers — avoids leaking
  record counts (e.g. a guessable `id=47` in a URL).

## Running locally
### Backend
```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
# create .env with DATABASE_URL, DIRECT_DATABASE_URL, JWT_SECRET_KEY
alembic upgrade head
uvicorn app.main:app --reload --reload-dir app
```

### Frontend
```powershell
cd frontend
npm install
# create .env with VITE_API_URL=http://127.0.0.1:8000
npm run dev
```

### Tests
```powershell
cd backend
pytest -v
```

## Demo credentials (deployed app)
| Role | Email | Password |
|---|---|---|
| Admin | admin@gmail.com | *(see submission notes)* |
| Member | shilpa@gmail.com | *(see submission notes)* |

## Task B
See the `task-b/` folder — `ASSESSMENT.md`, `MIGRATION_PLAN.md`,
`STANDARDS_PROPOSAL.md`, and a concrete before/after refactor in
`task-b/before/` and `task-b/after/`.

---

## API Reference
*(existing API documentation continues below, unchanged)*

# Lead Platform API

## Overview
A lead management API for a small sales team, with role-based access (admin/member),
a lead lifecycle pipeline, timestamped notes, and a full activity audit trail.

## Auth
All endpoints except `/public/leads`, `/auth/register`, and `/auth/login` require a
`Authorization: Bearer <token>` header, obtained from `/auth/login`.

## Roles
- **admin** — sees all leads, can create leads directly, assign any lead to any user
- **member** — sees only leads assigned to them, can update status and add notes, cannot assign

## Endpoints

### Auth
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | none | Create a user (email, password, role) |
| POST | `/auth/login` | none | Returns a JWT access token |

### Leads
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/leads` | admin | Create a lead |
| GET | `/leads` | any | List leads (paginated, filterable). Members see only their assigned leads. |
| GET | `/leads/{id}` | any | Get one lead. 404 if it doesn't exist *or* isn't visible to you. |
| PATCH | `/leads/{id}` | any (assignment: admin only) | Update status and/or assignment |
| POST | `/leads/{id}/notes` | any | Add a timestamped note |
| GET | `/leads/{id}/activity` | any | Full activity trail for a lead |

### Public
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/public/leads` | none | Public lead capture. Status/assignment fields are ignored if submitted. |

## `GET /leads` query parameters
- `page` (int, default 1)
- `page_size` (int, default 20, max 100)
- `status` (optional) — filter by one of: `new`, `contacted`, `qualified`, `won`, `lost`

## Status codes
| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Resource created |
| 400 | Bad request (e.g. assigning to a nonexistent user) |
| 401 | Missing/invalid/expired token |
| 403 | Authenticated, but not permitted (e.g. member trying to assign) |
| 404 | Not found — also returned when a member requests a lead they can't see, to avoid leaking existence |
| 422 | Request body failed validation |

## Example: full lifecycle
1. `POST /public/leads` — website visitor submits interest
2. Admin logs in, `GET /leads` to see it, `PATCH /leads/{id}` to assign it to a rep
3. Rep logs in, sees it in `GET /leads`, adds notes via `POST /leads/{id}/notes`,
   updates status via `PATCH /leads/{id}`
4. Anyone with access reviews `GET /leads/{id}/activity` for the full history
