# AWS Route53 Clone

A full-stack clone of the AWS Route 53 console experience. The app recreates
the main hosted-zone and DNS-record workflows with a Next.js frontend, FastAPI
backend, and SQLite persistence.

## Features

- Mocked authentication with login, logout, and local session persistence
- Hosted zone CRUD with search, pagination, edit modal, delete confirmation,
  and per-user persistence
- DNS record CRUD within a hosted zone
- Common Route 53 record types including A, AAAA, CNAME, TXT, MX, NS, PTR, SRV,
  CAA, DS, NAPTR, and SOA
- AWS-style navigation, tables, forms, modals, filters, and notifications
- Placeholder pages for the non-core Route 53 sections
- Bonus flows: BIND import, JSON/BIND export, dark mode, keyboard shortcuts,
  and bulk record deletion

## Project Structure

```text
backend/
  app/
    core/          Auth and app settings
    models/        SQLAlchemy models
    routers/       FastAPI route handlers
    schemas/       Pydantic request/response models
    services/      Service layer helpers
    repositories/  Database helper functions
frontend/
  app/             Next.js app router pages
  components/      Shared shell and UI components
  lib/             API client and auth context
```

## Setup

### Backend

```bash
cd backend
uv sync
```

Create `backend/.env`:

```env
SECRET_KEY=replace-with-a-local-secret
```

Run the API:

```bash
uv run uvicorn app.main:app --reload
```

The backend runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`.

Optional `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Architecture

The frontend keeps the AWS Route 53 console look and feel while calling the
FastAPI backend through `frontend/lib/api.ts`. Authentication uses the backend
login endpoint and stores the returned access token in local storage for the
mocked session. API requests include that token as a Bearer token.

The backend owns persistence through SQLAlchemy models and a local SQLite
database at `backend/route53.db`. Routes enforce user ownership for hosted
zones and DNS records, so each signed-in user sees only their own data.

## Database Schema

### `users`

- `id`
- `email`
- `name`
- `password_hash`
- `created_at`

### `refresh_tokens`

- `id`
- `user_id`
- `token_hash`
- `expires_at`
- `created_at`
- `revoked_at`

### `hosted_zones`

- `id`
- `user_id`
- `domain_name`
- `type`
- `description`
- `created_at`

### `dns_records`

- `id`
- `hosted_zone_id`
- `name`
- `type`
- `value`
- `ttl`
- `routing_policy`
- `created_at`

## API Overview

### Auth

- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`

### Hosted Zones

- `GET /hosted-zones/`
- `POST /hosted-zones/`
- `GET /hosted-zones/{zone_id}`
- `PUT /hosted-zones/{zone_id}`
- `DELETE /hosted-zones/{zone_id}`

### DNS Records

- `GET /hosted-zones/{zone_id}/records/`
- `POST /hosted-zones/{zone_id}/records/`
- `GET /hosted-zones/{zone_id}/records/{record_id}`
- `PUT /hosted-zones/{zone_id}/records/{record_id}`
- `DELETE /hosted-zones/{zone_id}/records/{record_id}`

## Verification

```bash
cd backend
uv run python -m compileall app

cd ../frontend
npm run build
```
