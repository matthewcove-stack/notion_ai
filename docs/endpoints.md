# V1 Endpoints

All endpoints are POST webhooks exposed by n8n. Every response uses the standard envelope from `INTENT.md`.

Auth header:

```
Authorization: Bearer <API_BEARER_TOKEN>
```

`/v1/os/bootstrap` is the only endpoint that uses `BOOTSTRAP_BEARER_TOKEN`.

## Endpoints

- `/v1/notion/search`
- `/v1/notion/tasks/create`
- `/v1/notion/tasks/update`
- `/v1/notion/lists/add_item`
- `/v1/notion/notes/capture`
- `/v1/notion/db/rows/create` (optional)

- `/v1/notion/db/schema`
- `/v1/notion/db/sample`

## Registry key mapping

Database keys resolve to OS Registry entries:

- `tasks` -> `tasks_db_id`
- `projects` -> `projects_db_id`
- `knowledge` -> `knowledge_db_id`
- `clients` -> `clients_db_id`
- `registry` -> `registry_db_id`
- `request_ledger` -> `ledger_db_id`
- `shopping_list` -> `shopping_list_db_id`
- `notes` -> `notes_db_id` (or reuse `knowledge_db_id`)

## Examples

### /v1/notion/search

Request:

```json
{
  "request_id": "uuid",
  "actor": "user",
  "payload": { "query": "OS", "limit": 10, "types": ["page", "database"] }
}
```

Response data:

```json
{
  "results": [
    { "id": "...", "object_type": "page", "title": "OS Root", "url": "...", "last_edited_time": "..." }
  ]
}
```

### /v1/notion/tasks/create

Request:

```json
{
  "request_id": "uuid",
  "idempotency_key": "abc123",
  "actor": "user",
  "payload": {
    "task": {
      "title": "Fix skirting",
      "due": "2026-01-18",
      "status": "Todo",
      "priority": "High",
      "project": "Bea Phase 2",
      "tags": ["carpentry"],
      "notes": "Order materials first"
    }
  }
}
```

Response data:

```json
{
  "created": true,
  "notion_page_id": "...",
  "notion_url": "..."
}
```

### /v1/notion/tasks/update

Request:

```json
{
  "request_id": "uuid",
  "idempotency_key": "def456",
  "actor": "user",
  "payload": {
    "notion_page_id": "...",
    "patch": {
      "status": "In Progress",
      "due": "2026-01-19",
      "priority": "Medium",
      "notes_append": "Started work"
    }
  }
}
```

Response data:

```json
{
  "updated": true,
  "notion_page_id": "...",
  "notion_url": "..."
}
```

### /v1/notion/lists/add_item

Request:

```json
{
  "request_id": "uuid",
  "idempotency_key": "ghi789",
  "actor": "user",
  "payload": {
    "list_item": {
      "list_key": "shopping_list",
      "item": "Milk",
      "notes": "2% preferred"
    }
  }
}
```

Response data:

```json
{
  "created": true,
  "notion_page_id": "...",
  "notion_url": "..."
}
```

### /v1/notion/notes/capture

Request:

```json
{
  "request_id": "uuid",
  "idempotency_key": "jkl012",
  "actor": "user",
  "payload": {
    "note": {
      "title": "Idea",
      "content": "Explore alternate onboarding flow",
      "tags": ["product", "ux"]
    }
  }
}
```

Response data:

```json
{
  "created": true,
  "notion_page_id": "...",
  "notion_url": "..."
}
```

### /v1/notion/db/schema

Request:

```json
{
  "request_id": "uuid",
  "actor": "user",
  "payload": { "database_key": "tasks" }
}
```

Response data:

```json
{
  "database_key": "tasks",
  "database_id": "...",
  "database_name": "Tasks",
  "properties": { "Title": { "type": "title" } },
  "last_edited_time": "..."
}
```

### /v1/notion/db/sample

Request:

```json
{
  "request_id": "uuid",
  "actor": "user",
  "payload": { "database_key": "tasks", "limit": 25 }
}
```

Optional filter (supported subset):

```json
{
  "request_id": "uuid",
  "actor": "user",
  "payload": {
    "database_key": "tasks",
    "limit": 10,
    "filter": { "property": "Status", "type": "select", "equals": "Todo" }
  }
}
```

Response data:

```json
{
  "database_key": "tasks",
  "database_id": "...",
  "results": [
    { "id": "...", "url": "...", "properties": { "Title": "Fix skirting" } }
  ]
}
```

## Token rotation

1) Generate a new random token.
2) Update `.env` with the new value (either `BOOTSTRAP_BEARER_TOKEN` or `API_BEARER_TOKEN`).
3) Restart n8n: `docker compose up -d`.
4) Update any clients that call the endpoints.

# Public Webhook URLs

Base: https://glibly-ungravitational-mckayla.ngrok-free.dev

- /v1/notion/tasks/update
  https://glibly-ungravitational-mckayla.ngrok-free.dev/webhook/Lamgvb3jcOzLyPnt/webhook/v1/notion/tasks/update
- /v1/os/bootstrap
  https://glibly-ungravitational-mckayla.ngrok-free.dev/webhook/7bxdnVN9oF933Pdo/webhook/v1/os/bootstrap
- /v1/notion/search
  https://glibly-ungravitational-mckayla.ngrok-free.dev/webhook/xWiRSQAZK0sOahE0/webhook/v1/notion/search
- /v1/notion/db/schema
  https://glibly-ungravitational-mckayla.ngrok-free.dev/webhook/Gtl8o5343hhkJQfb/webhook/v1/notion/db/schema
- /v1/notion/tasks/create
  https://glibly-ungravitational-mckayla.ngrok-free.dev/webhook/G6rgkPl3FjDzGKmk/webhook/v1/notion/tasks/create
- /v1/notion/db/sample
  https://glibly-ungravitational-mckayla.ngrok-free.dev/webhook/JZdSG9jUOXGLdHVc/webhook/v1/notion/db/sample
