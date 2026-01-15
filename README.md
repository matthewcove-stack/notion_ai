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

## Repository layout

- `INTENT.md` - Canonical spec and requirements
- `schemas/` - Schema-as-code JSON definitions (future)
- `.github/` - Issue templates and CI

## Status

Work in progress. No automated tests configured yet.
