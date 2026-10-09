from datetime import datetime, timezone
from typing import Callable
from uuid import uuid4


def order_event(order_id: str, stage: str, customer_id: str, **details) -> dict:
    """Create the stable event shape used for every order transition."""
    return {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "checkout-worker",
        "message": f"order {order_id} reached {stage}",
        "order_id": order_id,
        "stage": stage,
        "customer_id": customer_id,
        "details": details,
    }


def ship_order(order_id: str, customer_id: str, send: Callable[[dict], dict]) -> list[dict]:
    """Record the customer-visible order path, in order, and return sent events."""
    stages = [
        ("checkout", {"cart_total": 1299, "currency": "USD"}),
        ("fulfillment", {"warehouse": "east-1"}),
        ("receipt", {"channel": "email"}),
        ("customer_update", {"status": "shipped"}),
    ]
    sent = []
    for stage, details in stages:
        event = order_event(order_id, stage, customer_id, **details)
        send(event)
        sent.append(event)
    return sent
