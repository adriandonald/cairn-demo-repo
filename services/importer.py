"""Bulk order import service.

Processes CSV-formatted order data submitted by operations staff,
validates each row, and creates orders in bulk via the OrderService.
"""

from typing import Any

from services.orders import OrderService

_order_service = OrderService()

REQUIRED_FIELDS = {"user_id", "product_id", "quantity", "shipping_address"}


def import_orders_from_csv(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Import a batch of orders from parsed CSV rows.

    Validates each row against the required field set and creates an
    order for each valid row. Invalid rows are collected and returned
    in the result summary rather than failing the entire batch.

    Args:
        rows: List of dicts parsed from CSV, one per order line.

    Returns:
        Dict with keys: created (list of order dicts),
        failed (list of {row, reason} dicts), total, success_count.
    """
    created = []
    failed = []

    for i, row in enumerate(rows):
        missing = REQUIRED_FIELDS - set(row.keys())
        if missing:
            failed.append({"row": i, "reason": f"Missing fields: {missing}"})
            continue

        try:
            quantity = int(row["quantity"])
        except (ValueError, TypeError):
            failed.append({"row": i, "reason": "quantity must be an integer"})
            continue

        if quantity < 1:
            failed.append({"row": i, "reason": "quantity must be at least 1"})
            continue

        try:
            order = _order_service.create_order(
                user_id=str(row["user_id"]),
                items=[{"product_id": row["product_id"], "quantity": quantity}],
                shipping_address=str(row["shipping_address"]),
            )
            created.append(order)
        except Exception as exc:
            failed.append({"row": i, "reason": str(exc)})

    return {
        "total": len(rows),
        "success_count": len(created),
        "created": created,
        "failed": failed,
    }
