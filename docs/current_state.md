# notion_gateway — Current State (Authoritative for this repo)

## What works today
- Local n8n + Postgres compose environment
- Schema-as-code under `schemas/`
- Webhook endpoints for bootstrap, search, tasks create/update, db schema/sample (per README)
- Additional Phase 2 mutation endpoints:
  - `POST /v1/notion/lists/add_item`
  - `POST /v1/notion/notes/capture`
- Smoke tests exist (`docker compose run --rm smoke all`)

## What must be true for Brain OS Phase 1
- `POST /v1/notion/tasks/create` returns a stable Notion page/task identifier and is idempotent for the same request_id.
- `POST /v1/notion/tasks/update` updates the correct task deterministically.
- Both endpoints authenticate using bearer tokens as documented.

## Phase 1 scope (exact)

Goal: a single end-to-end vertical slice that reliably turns a natural-language intent into a Notion Task create/update, with an audit trail.

In scope:
- Submit intent (via action_relay client or curl) to intent_normaliser `POST /v1/intents`.
- intent_normaliser normalises into a deterministic plan (`notion.tasks.create` or `notion.tasks.update`).
- If `EXECUTE_ACTIONS=true` and confidence >= threshold, intent_normaliser executes the plan by calling notion_gateway:
  - `POST /v1/notion/tasks/create` or `POST /v1/notion/tasks/update`
- Write artifacts for: received → normalised → executed (or failed) with stable IDs.
- Idempotency: duplicate submissions with the same `request_id` (or generated deterministic key) must not create duplicate Notion tasks.
- Error handling: gateway errors are surfaced in the response and recorded as artifacts.
- Minimal context lookups:
  - Optional: query context_api for project/task hints when provided, but Phase 1 must still work without context_api being “perfect”.

Out of scope (Phase 2+):
- UI for clarifications (API-only is fine).
- Calendar events / reminders.
- Full automated background sync from Notion.
- Multi-user, permissions, or “agents” beyond single operator.


## Verification commands
- Smoke tests (Docker-only):
  - `docker compose up -d`
  - `docker compose run --rm smoke all`
