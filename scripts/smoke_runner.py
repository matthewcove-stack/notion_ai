#!/usr/bin/env python3
import json
import os
import sys
import time
import uuid
from urllib import request, error


def get_api_token():
    token = os.environ.get("API_BEARER_TOKEN")
    if not token:
        raise RuntimeError("Missing API_BEARER_TOKEN")
    return token


def get_bootstrap_token():
    token = os.environ.get("BOOTSTRAP_BEARER_TOKEN")
    if not token:
        raise RuntimeError("Missing BOOTSTRAP_BEARER_TOKEN")
    return token


def base_url():
    return os.environ.get("SMOKE_BASE_URL", "http://n8n:5678").rstrip("/")


def n8n_api_key():
    return os.environ.get("N8N_API_KEY")


def n8n_api_base():
    return os.environ.get("SMOKE_N8N_API_BASE", base_url())


def resolve_workflow_prefix_map():
    mapping = os.environ.get("SMOKE_WEBHOOK_MAP")
    if not mapping:
        return {}
    try:
        return json.loads(mapping)
    except json.JSONDecodeError:
        raise RuntimeError("SMOKE_WEBHOOK_MAP must be valid JSON")


def fetch_workflow_ids():
    api_key = n8n_api_key()
    if not api_key:
        return {}
    url = f"{n8n_api_base()}/api/v1/workflows"
    req = request.Request(url, method="GET")
    req.add_header("X-N8N-API-KEY", api_key)
    with request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    workflows = data.get("data", [])
    latest = {}
    for wf in workflows:
        name = wf.get("name")
        if not name:
            continue
        if wf.get("active") is False:
            continue
        updated = wf.get("updatedAt") or ""
        if name not in latest or updated > latest[name]["updatedAt"]:
            latest[name] = {"id": wf.get("id"), "updatedAt": updated}
    return {name: info["id"] for name, info in latest.items()}


def webhook_url_for(endpoint):
    prefix = os.environ.get("SMOKE_WEBHOOK_PREFIX", "").strip("/")
    if prefix:
        return f"{base_url()}/webhook/{prefix}{endpoint}"

    prefix_map = resolve_workflow_prefix_map()
    if endpoint in prefix_map:
        map_prefix = str(prefix_map[endpoint]).strip("/")
        return f"{base_url()}/webhook/{map_prefix}{endpoint}"

    workflow_map = {
        "/v1/os/bootstrap": "v1_os_bootstrap",
        "/v1/notion/search": "v1_notion_search",
        "/v1/notion/tasks/create": "v1_tasks_create",
        "/v1/notion/tasks/update": "v1_tasks_update",
        "/v1/notion/db/schema": "v1_db_schema",
        "/v1/notion/db/sample": "v1_db_sample",
    }
    workflow_name = workflow_map.get(endpoint)
    workflow_ids = fetch_workflow_ids()
    workflow_id = workflow_ids.get(workflow_name)
    if workflow_id:
        return f"{base_url()}/webhook/{workflow_id}/webhook{endpoint}"

    return f"{base_url()}/webhook{endpoint}"


def post_json(path, payload, token):
    url = webhook_url_for(path)
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    try:
        with request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, body
    except error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


def envelope(request_id, actor, payload, idempotency_key=None):
    body = {
        "request_id": request_id,
        "actor": actor,
        "payload": payload,
    }
    if idempotency_key:
        body["idempotency_key"] = idempotency_key
    return body


def parse_json(body):
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def assert_ok(status, body, label):
    if status != 200:
        raise RuntimeError(f"{label} failed with HTTP {status}: {body}")
    data = parse_json(body)
    if not data or data.get("status") != "ok":
        raise RuntimeError(f"{label} returned error: {body}")
    return data


def run_bootstrap(token):
    payload = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        idempotency_key="smoke-bootstrap",
        payload={"schema_version": 1, "rebuild": False},
    )
    status, body = post_json("/v1/os/bootstrap", payload, token)
    data = assert_ok(status, body, "bootstrap")
    created = data["data"]["created"]
    return created


def run_search(token):
    payload = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        payload={"query": "OS", "limit": 5, "types": ["page", "database"]},
    )
    status, body = post_json("/v1/notion/search", payload, token)
    data = assert_ok(status, body, "search")
    results = data["data"]["results"]
    for row in results:
        print(json.dumps(row))
    return results


def run_db_schema(token, key):
    payload = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        payload={"database_key": key},
    )
    status, body = post_json("/v1/notion/db/schema", payload, token)
    data = assert_ok(status, body, "db_schema")
    return data["data"]


def run_db_sample(token, key):
    payload = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        payload={"database_key": key, "limit": 3},
    )
    status, body = post_json("/v1/notion/db/sample", payload, token)
    data = assert_ok(status, body, "db_sample")
    return data["data"]["results"]


def run_task_create(token):
    key = f"smoke-task-create-{uuid.uuid4()}"
    task = {
        "title": f"Smoke Task {int(time.time())}",
        "status": "Todo",
        "priority": "Low",
        "tags": ["smoke"],
        "notes": "Smoke test create",
    }
    payload = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        idempotency_key=key,
        payload={"task": task},
    )
    status, body = post_json("/v1/notion/tasks/create", payload, token)
    data = assert_ok(status, body, "tasks_create")

    replay = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        idempotency_key=key,
        payload={"task": task},
    )
    status2, body2 = post_json("/v1/notion/tasks/create", replay, token)
    data2 = assert_ok(status2, body2, "tasks_create_replay")

    if data["data"]["created"] is not True:
        raise RuntimeError("tasks_create expected created=true")
    if data2["data"]["created"] is not False:
        raise RuntimeError("tasks_create replay expected created=false")

    return data["data"]["notion_page_id"]


def run_task_update(token, page_id):
    key = f"smoke-task-update-{uuid.uuid4()}"
    patch = {
        "status": "In Progress",
        "notes_append": "Smoke update append",
    }
    payload = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        idempotency_key=key,
        payload={"notion_page_id": page_id, "patch": patch},
    )
    status, body = post_json("/v1/notion/tasks/update", payload, token)
    data = assert_ok(status, body, "tasks_update")

    replay = envelope(
        request_id=str(uuid.uuid4()),
        actor="smoke",
        idempotency_key=key,
        payload={"notion_page_id": page_id, "patch": patch},
    )
    status2, body2 = post_json("/v1/notion/tasks/update", replay, token)
    data2 = assert_ok(status2, body2, "tasks_update_replay")

    if data["data"]["updated"] is not True:
        raise RuntimeError("tasks_update expected updated=true")
    if data2["data"]["updated"] is not False:
        raise RuntimeError("tasks_update replay expected updated=false")


def main():
    api_token = get_api_token()
    command = sys.argv[1] if len(sys.argv) > 1 else "all"

    if command == "bootstrap":
        created = run_bootstrap(get_bootstrap_token())
        print(f"bootstrap created={created}")
        return

    if command == "search":
        results = run_search(api_token)
        print(f"search results={len(results)}")
        return

    if command == "tasks":
        page_id = run_task_create(api_token)
        print(f"tasks_create page_id={page_id}")
        run_task_update(api_token, page_id)
        print("tasks_update ok")
        return

    if command == "db":
        schema = run_db_schema(api_token, "tasks")
        print(f"db_schema id={schema['database_id']}")
        sample = run_db_sample(api_token, "tasks")
        print(f"db_sample rows={len(sample)}")
        return

    if command != "all":
        raise RuntimeError(f"Unknown command: {command}")

    created = run_bootstrap(get_bootstrap_token())
    print(f"bootstrap created={created}")
    results = run_search(api_token)
    print(f"search results={len(results)}")
    page_id = run_task_create(api_token)
    print(f"tasks_create page_id={page_id}")
    run_task_update(api_token, page_id)
    print("tasks_update ok")
    schema = run_db_schema(api_token, "tasks")
    print(f"db_schema id={schema['database_id']}")
    sample = run_db_sample(api_token, "tasks")
    print(f"db_sample rows={len(sample)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc))
        sys.exit(1)
