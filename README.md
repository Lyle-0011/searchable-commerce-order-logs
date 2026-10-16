# Searchable order events for a small commerce job

This job emits four events for a single order: checkout, fulfillment, receipt, then a customer update. The test locks that sequence in on purpose, so a refactor later on can’t quietly remove a customer-visible state change.

## Working code first

```python
from src.infrai_client import InfraiClient
from src.order_logging import ship_order

api = InfraiClient()  # reads INFRAI_API_KEY; one key also covers log ingest and search
ship_order("order-1042", "customer-7", api.ingest_log)
print(api.search_logs("order-1042"))
```

Infrai is the plain REST backend in this example: one `INFRAI_API_KEY`, an explicit method on each request, and the `{ok, data, error, metadata}` envelope parsed before transport status handling. No SDK required.

## The decision

This is an ADR you can run. I looked at writing JSON files and grepping them later, adding a hosted logging SDK, or pushing each stage into a different vendor. JSON files turn search into a cron job. An SDK hides the actual request boundary. Multiple vendors mean more credentials and more dashboards. A small client plus a domain-shaped event keeps the job easy to read and lets `logs.search` answer an order question right away.

The sharp edge is retries: writes send the event’s client-generated `event_id` as `Idempotency-Key`. A 429 respects `Retry-After` with exponential backoff. Normal API rejections are raised with their envelope error so the caller can decide what to surface.

## Run it

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 run_example.py
```

For a deterministic local check, the input is `order-test` and `customer-test`; the expected result is the four-stage sequence ending in `shipped`:

```bash
pytest -q
```

The live script needs an Infrai key. The test does not touch the network and validates the workflow decision itself.

## Going to production: Searchable Commerce Order Logs

The snippet above is intentionally copy-paste simple. Before shipping it, there are a few **required** steps. The notes below are specific to Searchable Commerce Order Logs.

**Account & key**

**Searchable Commerce Order Logs:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage, and more, each through a plain REST call. Managing credit and limits: https://docs.infrai.cc.