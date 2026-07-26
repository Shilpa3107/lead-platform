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
