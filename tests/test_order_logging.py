from src.order_logging import ship_order


def test_order_path_is_customer_visible_and_ordered():
    sent = []
    events = ship_order("order-test", "customer-test", lambda event: sent.append(event))
    assert [event["stage"] for event in events] == ["checkout", "fulfillment", "receipt", "customer_update"]
    assert sent == events
    assert events[-1]["details"]["status"] == "shipped"
