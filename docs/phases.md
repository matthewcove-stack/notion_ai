# notion_gateway — Phases

## Phase 0 (done)
- Kernel endpoints and schema-as-code
- n8n workflow exports and local compose
- Basic smoke test harness

## Phase 1 (kernel responsibilities)
- Confirm and enforce idempotency for task create/update using request_id
- Ensure response payload includes the created/updated task ID in a stable field
- Ensure error responses are consistent and machine-readable

## Phase 2 (later)
- Expanded entity support (CRM, knowledge capture, finance)
- More rigorous contract tests against notion_assistant_contracts

---

## MVP to Market alignment

See `brain_os/docs/mvp_to_market.md`.

### Phase 2 (broader actions)
Add endpoints + workflows:
- `/v1/notion/lists/add_item`
- `/v1/notion/notes/capture`
- (optional) `/v1/notion/db/rows/create`

Ensure responses return Notion IDs/URLs where possible and write to the request ledger for idempotency support.
