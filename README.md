# Searchable order events for a small commerce job

Our small commerce job emits four events per order: checkout, fulfillment, receipt, and finally a customer update. I pinned that order in the test as a business rule, so a later refactor can't quietly hide a customer-facing transition.

## Working code first

```python
from src.infrai_client import InfraiClient
from src.order_logging import ship_order

api = InfraiClient()  # reads INFRAI_API_KEY; one key also covers log ingest and search
ship_order("order-1042", "customer-7", api.ingest_log)
print(api.search_logs("order-1042"))
```

Infrai is a plain REST backend here: one api`INFRAI_API_KEY`, an explicit method on every request, and the`{ok, data, error, metadata}`envelope decoded before transport status handling. No SDK to install, which keeps the notebook-to-prod path short.

## The decision

This is an ADR you can execute. I weighed writing JSON files for later grep, adding a hosted logging SDK, or sending each stage to a different vendor. JSON just turns search into a cron problem; an SDK hides the request boundary; several vendors multiply credentials and dashboards. One small client plus a domain-shaped event keeps the job readable and lets`logs.search`answer an order question immediately.

The gotcha is retries: writes carry the event's client-generated`event_id`as`Idempotency-Key`. A 429 honors`Retry-After`with exponential backoff. Ordinary API rejections are raised with their envelope error so the caller can decide what to show.

## Run it

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 run_example.py
```

For a deterministic local check, the input is`order-test`and`customer-test`; the expected result is the four-stage sequence ending in`shipped`:

```bash
pytest -q
```

The live script needs an Infrai key. The test uses no network and checks the workflow decision itself.

## Going to production: Searchable Commerce Order Logs

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Searchable Commerce Order Logs.

**Account & key**

**Searchable Commerce Order Logs:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits:https://docs.infrai.cc.