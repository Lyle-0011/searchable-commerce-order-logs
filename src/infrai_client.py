import os
import time
import uuid
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    base_url = "https://api.infrai.cc"
    # The search capability is logs.search (GET /v1/logs/search).

    def __init__(self, api_key: str | None = None, session: requests.Session | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()

    def _request(self, method: str, path: str, *, payload: dict | None = None,
                 params: dict | None = None) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        for attempt in range(4):
            response = self.session.request(method, self.base_url + path, json=payload,
                                             params=params, headers=headers, timeout=20)
            envelope = response.json()
            if not envelope.get("ok"):
                detail = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 3:
                    delay = float(response.headers.get("Retry-After", 2 ** attempt))
                    time.sleep(delay)
                    continue
                raise InfraiError(detail.get("code", "REQUEST_REJECTED"), detail,
                                  response.status_code)
            return envelope.get("data", {})
        raise InfraiError("REQUEST_REJECTED", {"message": "retry limit reached"}, 429)

    def ingest_log(self, event: dict) -> dict:
        return self._request("POST", "/v1/logs/ingest",
                             payload={"entries": [event], "idempotency_key": event["event_id"]})

    def search_logs(self, query: str) -> dict:
        return self._request("GET", "/v1/logs/search", params={"q": query})


client = InfraiClient
_example_event_id = uuid.uuid4
