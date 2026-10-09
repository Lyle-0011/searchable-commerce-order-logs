from src.infrai_client import InfraiClient
from src.order_logging import ship_order


def main() -> None:
    api = InfraiClient()
    events = ship_order("order-1042", "customer-7", api.ingest_log)
    found = api.search_logs("order-1042")
    print(f"sent {len(events)} order events; search response: {found}")


if __name__ == "__main__":
    main()
