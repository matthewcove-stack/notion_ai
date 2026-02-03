# UC01 - Task Capture (notion_gateway)

UC01 is the Phase 1 vertical slice: natural language -> Notion task (create/update).

## Responsibilities
`notion_gateway` is the Notion OS kernel providing stable, authenticated HTTP endpoints for Notion mutations.

For UC01, it must:
1. Expose task create/update endpoints used by `intent_normaliser`:
   - `POST /v1/notion/tasks/create`
   - `POST /v1/notion/tasks/update`
2. Enforce bearer token authentication.
3. Be idempotent by `request_id`.
4. Return a stable Notion task identifier in the standard response envelope.

## Contract highlights

### Auth
All UC01 requests use:

- `Authorization: Bearer <API_BEARER_TOKEN>`

### Request envelope
The gateway expects a wrapper envelope:

```json
{
  "request_id": "uuid",
  "idempotency_key": "action:...",
  "actor": "user-or-service",
  "payload": { ... }
}
```

### Create task
`POST /v1/notion/tasks/create`

Payload shape:

```json
{
  "payload": {
    "task": {
      "title": "...",
      "due": "YYYY-MM-DD",
      "status": "Todo",
      "priority": "High",
      "project": "...",
      "tags": ["..."],
      "notes": "..."
    }
  }
}
```

Response must include:
- `data.notion_page_id` (or an equivalent stable task id field)

### Update task
`POST /v1/notion/tasks/update`

Payload shape:

```json
{
  "payload": {
    "notion_page_id": "...",
    "patch": {
      "status": "Done",
      "due": "YYYY-MM-DD",
      "priority": "Medium",
      "notes_append": "..."
    }
  }
}
```

Response must include:
- `data.notion_page_id`

## Idempotency (Phase 1)
- For the same `request_id`, create must return the same `data.notion_page_id`.
- This is typically implemented using the request ledger database/workflow.

## Errors
Failures must be machine-readable in the standard envelope:
- `status: "error"`
- `error.code`
- `error.message`
- optional `error.details.status_code`

## Verification
- `docker compose up -d`
- `docker compose run --rm smoke all`
