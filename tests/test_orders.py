"""Tests for OrderService including order cancellation.

Covers the cancel_order method added in feat/add-order-cancellation.
Uses the in-memory store directly -- no network calls.
"""

import pytest

from services.orders import OrderService


@pytest.fixture()
def service() -> OrderService:
    return OrderService()


@pytest.fixture()
def pending_order(service: OrderService) -> dict:
    return service.create_order(
        user_id="user-1",
        items=[{"product_id": "p1", "quantity": 2}],
        shipping_address="1 Test Street",
    )


def test_cancel_pending_order(service: OrderService, pending_order: dict) -> None:
    result = service.cancel_order(pending_order["id"], "user-1")
    assert result is not None
    assert result["status"] == "cancelled"
    assert "cancelled_at" in result


def test_cancel_returns_none_for_wrong_user(
    service: OrderService, pending_order: dict
) -> None:
    result = service.cancel_order(pending_order["id"], "other-user")
    assert result is None


def test_cancel_returns_none_for_missing_order(service: OrderService) -> None:
    result = service.cancel_order("nonexistent-id", "user-1")
    assert result is None


def test_cancel_shipped_order_raises(service: OrderService, pending_order: dict) -> None:
    pending_order["status"] = "shipped"
    with pytest.raises(ValueError, match="cannot be cancelled"):
        service.cancel_order(pending_order["id"], "user-1")


def test_cancel_delivered_order_raises(
    service: OrderService, pending_order: dict
) -> None:
    pending_order["status"] = "delivered"
    with pytest.raises(ValueError, match="cannot be cancelled"):
        service.cancel_order(pending_order["id"], "user-1")
