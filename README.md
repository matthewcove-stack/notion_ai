# Notion OS Kernel

Production-grade Notion "OS" kernel that bootstraps a canonical workspace, provisions deterministic schemas, and exposes stable HTTPS JSON endpoints for ChatGPT in standard user mode.

## What this repo is for

- Define the canonical workspace model and system databases
- Specify stable API contracts and idempotent workflows
- Keep Notion as the state store while n8n executes changes

See `INTENT.md` for the full specification.

## High-level endpoints

- `POST /v1/os/bootstrap`
- `POST /v1/notion/search`
- `POST /v1/notion/tasks/create`
- `POST /v1/notion/tasks/update`
- `POST /v1/notion/db/schema`
- `POST /v1/notion/db/sample`

## How to run locally

1) Create a local env file:

```bash
cp .env.example .env
```

2) Edit `.env` and set:

- `N8N_BASIC_AUTH_USER` / `N8N_BASIC_AUTH_PASSWORD`
- `N8N_ENCRYPTION_KEY` (32+ chars)
- `NOTION_API_KEY` (Notion internal integration token)
- `BOOTSTRAP_BEARER_TOKEN` (shared secret for all v1 endpoints)
- `API_BEARER_TOKEN` (fallback if bootstrap token is not set)
- `NODE_FUNCTION_ALLOW_BUILTIN` should include `fs,path` for schema-as-code access

3) Start n8n + Postgres:

```bash
docker compose up -d
```

The compose file mounts `./schemas` into the container at `/files/schemas`.

4) Open the editor:

```
http://localhost:5678
```

## How to import the workflows

1) In n8n, go to Workflows -> Import from File.
2) Select the workflow JSON files in `n8n/workflows/` and `n8n/workflows/_core/`.
3) Save and activate each workflow.

The webhook endpoint will be:

```
POST http://localhost:5678/webhook/v1/os/bootstrap
```

Include header:

```
Authorization: Bearer <BOOTSTRAP_BEARER_TOKEN>
```

## Smoke tests (Docker-only)

```bash
docker compose up -d
docker compose run --rm smoke all
```

If n8n registers webhooks with workflow ID prefixes, either set `N8N_API_KEY` in `.env` (recommended) or provide a prefix override:

```
SMOKE_WEBHOOK_PREFIX=<workflow_id>/webhook
```

## Repository layout

- `INTENT.md` - Canonical spec and requirements
- `schemas/` - Schema-as-code JSON definitions
- `n8n/workflows/` - Exported n8n workflow JSON
- `scripts/` - Local helper scripts
- `docs/` - Supplemental docs
- `.github/` - Issue templates and CI

## Endpoints

### /v1/notion/search

POST `/v1/notion/search` with header:

```
Authorization: Bearer <API_BEARER_TOKEN>
```

Payload:

```json
{
  "request_id": "uuid",
  "actor": "string",
  "payload": { "query": "text", "limit": 10, "types": ["page","database"] }
}
```

See `docs/endpoints.md` for request/response examples, registry key mapping, and token rotation.

## Shared idempotency core

Reusable sub-workflows live in `n8n/workflows/_core/`:

- `idempotency_check.json`
- `idempotency_commit.json`

These are called by mutating endpoints to ensure deterministic replay behavior.

## Required environment variables

- `NOTION_API_KEY`
- `API_BEARER_TOKEN`
- `N8N_API_KEY` (required for docker smoke tests to resolve workflow webhook IDs)
