# intent.md — Notion OS Kernel (Deterministic n8n Gateway)

## 1) Purpose

Build a **production-grade Notion Operating System Kernel** that:

• Bootstraps a **canonical OS Root page** inside an existing Notion workspace  
• Provisions all canonical pages and databases deterministically beneath it  
• Exposes a small set of stable HTTPS JSON endpoints (“tools”) for ChatGPT running strictly in normal (non-dev) mode  
• Makes Notion a programmable **state store / memory substrate**  
• Enforces deterministic, auditable, AI-native workflows  

ChatGPT = reasoning cockpit  
n8n = execution kernel  
Notion = state store  

---

## 2) Hard Constraints

• ChatGPT runs in **standard user mode only**  
• No plugins, no beta integrations, no dev tools  
• All side-effects occur via HTTPS JSON calls to n8n  
• The system operates **inside an existing Notion workspace** (Notion API cannot create workspaces)

---

## 3) API Contracts

### 3.1 Request Envelope (mandatory)

```json
{
  "request_id": "uuid",
  "idempotency_key": "string",
  "actor": "chatgpt",
  "payload": {}
}
```

`idempotency_key` is **required for all mutating endpoints**.

---

### 3.2 Response Envelope (mandatory)

```json
{
  "request_id": "uuid",
  "status": "ok | error",
  "correlation_id": "n8n-exec-id",
  "data": {},
  "error": { "code": "...", "message": "...", "details": {} }
}
```

HTTP Status Codes: `200, 400, 401, 409, 500`

---

## 4) Canonical Workspace Model

Everything lives under one deterministic root:

```
/OS Root
    /Databases
    /Projects
    /Knowledge
    /Clients
    /Archive
    /System
```

No pre-existing structure is assumed.

---

## 5) Required System Databases

Under `/System`, bootstrap must provision:

### 5.1 OS Registry (single-row DB)

Stores canonical IDs and schema version:

| key | value |
|----|------|
| root_page_id | notion id |
| tasks_db_id | notion id |
| schema_version | integer |
| last_bootstrap_run | timestamp |

---

### 5.2 Request Ledger

Used for idempotency & audit:

| idempotency_key | request_id | endpoint | result_page_id | status | timestamp |

All mutating operations must consult and write to this ledger.

---

## 6) Schema-as-Code

All canonical database schemas live in:

```
/schemas/*.json
```

Bootstrap provisions databases from these files:

- schemas/tasks.json  
- schemas/projects.json  
- schemas/knowledge.json  
- schemas/clients.json  
- schemas/registry.json  
- schemas/request_ledger.json  

No hard-coded schema in workflows.

---

## 7) Mandatory v1 Endpoints

| Endpoint | Purpose |
|---------|--------|
| /v1/os/bootstrap | Provision OS Root, all pages, all DBs, registry |
| /v1/notion/search | Workspace search |
| /v1/notion/tasks/create | Create task |
| /v1/notion/tasks/update | Update task |
| /v1/notion/db/schema | Return schema for a database_key |
| /v1/notion/db/sample | Return sample rows |

---

## 8) /v1/os/bootstrap

Bootstraps entire OS from schema files.

Payload:
```json
{
  "schema_version": 1,
  "rebuild": false
}
```

Behavior:
• If registry empty → provision  
• If registry exists and version matches → NOOP  
• If version lower → return upgrade_required  

Must write all IDs into OS Registry.

---

## 9) /v1/notion/tasks/create

Creates task in canonical Tasks DB.

Payload:
```json
{
  "task": {
    "title": "Fix skirting",
    "due": "2026-01-18",
    "status": "Todo",
    "priority": "High",
    "project": "Bea Phase 2",
    "tags": ["carpentry"]
  }
}
```

Must enforce idempotency via Request Ledger.

---

## 10) /v1/notion/search

Mandatory.

Payload:
```json
{
  "query": "Bea",
  "limit": 10,
  "types": ["page","database"]
}
```

---

## 11) Security

• Bearer token auth only (v1)  
• All endpoints require Authorization header  
• Secrets stored in n8n only  
• No secrets committed to repo  

---

## 12) Observability

All executions must log:

• request_id  
• idempotency_key  
• endpoint  
• correlation_id  
• notion object id (if applicable)

---

## 13) Definition of Done

• Fresh workspace can be bootstrapped from nothing  
• OS Root and canonical pages created  
• All databases provisioned from schema files  
• Registry + ledger operational  
• Search operational  
• Create/update task operational  
• All endpoints idempotent  
• Smoke tests pass  
