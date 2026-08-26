"""Tests for OrderService including order cancellation.

Covers the cancel_order method added in feat/add-order-cancellation.
Uses the in-memory store directly -- no network calls.
"""

import pytest

from services.orders import OrderService


@pytest.fixture()
def service() -> OrderService:
    """Return a fresh OrderService instance."""
    return OrderService()


@pytest.fixture()
def pending_order(service: OrderService) -> dict[str, object]:
    """Return a newly created pending order owned by user-1."""
    return service.create_order(
        user_id="user-1",
        items=[{"product_id": "p1", "quantity": 2}],
        shipping_address="1 Test Street",
    )


def test_cancel_pending_order(
    service: OrderService, pending_order: dict[str, object]
) -> None:
    """Cancelling a pending order sets status to cancelled and records a timestamp."""
    result = service.cancel_order(str(pending_order["id"]), "user-1")
    assert result is not None
    assert result["status"] == "cancelled"
    assert "cancelled_at" in result


def test_cancel_returns_none_for_wrong_user(
    service: OrderService, pending_order: dict[str, object]
) -> None:
    """cancel_order returns None when the requesting user does not own the order."""
    result = service.cancel_order(str(pending_order["id"]), "other-user")
    assert result is None


def test_cancel_returns_none_for_missing_order(service: OrderService) -> None:
    """cancel_order returns None for an order ID that does not exist."""
    result = service.cancel_order("nonexistent-id", "user-1")
    assert result is None


def test_cancel_shipped_order_raises(
    service: OrderService, pending_order: dict[str, object]
) -> None:
    """cancel_order raises ValueError when the order has already shipped."""
    pending_order["status"] = "shipped"
    with pytest.raises(ValueError, match="cannot be cancelled"):
        service.cancel_order(str(pending_order["id"]), "user-1")


def test_cancel_delivered_order_raises(
    service: OrderService, pending_order: dict[str, object]
) -> None:
    """cancel_order raises ValueError when the order has already been delivered."""
    pending_order["status"] = "delivered"
    with pytest.raises(ValueError, match="cannot be cancelled"):
        service.cancel_order(str(pending_order["id"]), "user-1")


def test_cancel_confirmed_order(
    service: OrderService, pending_order: dict[str, object]
) -> None:
    """Confirmed orders are also cancellable before shipping."""
    pending_order["status"] = "confirmed"
    result = service.cancel_order(str(pending_order["id"]), "user-1")
    assert result is not None
    assert result["status"] == "cancelled"
