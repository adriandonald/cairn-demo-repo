"""Order service.

Handles business logic for creating, retrieving, managing, and
cancelling orders. In this demo the store is an in-memory dict;
a real implementation would use the database layer in db/.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# In-memory store for demo purposes
_ORDERS: dict[str, dict[str, Any]] = {}

CANCELLABLE_STATUSES = {"pending", "confirmed"}


class OrderService:
    """Provides order management operations for the API layer."""

    def get_orders_for_user(self, user_id: str) -> list[dict[str, Any]]:
        """Return all orders belonging to a user.

        Args:
            user_id: The user's identifier string.

        Returns:
            List of order dicts, newest first.
        """
        orders = [o for o in _ORDERS.values() if o["user_id"] == user_id]
        return sorted(orders, key=lambda o: o["created_at"], reverse=True)

    def get_order(self, order_id: int, user_id: str) -> dict[str, Any] | None:
        """Return a single order if it belongs to the user.

        Args:
            order_id: Integer order identifier.
            user_id: The requesting user's identifier.

        Returns:
            Order dict, or None if not found or not owned by user.
        """
        order = _ORDERS.get(str(order_id))
        if order is None or order["user_id"] != user_id:
            return None
        return order

    def create_order(
        self,
        user_id: str,
        items: list[dict[str, Any]],
        shipping_address: str,
    ) -> dict[str, Any]:
        """Create and persist a new order.

        Args:
            user_id: The ordering user's identifier.
            items: List of {product_id, quantity} dicts.
            shipping_address: Delivery address string.

        Returns:
            The newly created order dict including its assigned id.
        """
        order_id = str(uuid.uuid4())
        order: dict[str, Any] = {
            "id": order_id,
            "user_id": user_id,
            "items": items,
            "shipping_address": shipping_address,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _ORDERS[order_id] = order
        logger.info("Order %s created with %d items", order_id, len(items))
        return order

    def cancel_order(
        self, order_id: str, user_id: str
    ) -> dict[str, Any] | None:
        """Cancel an order if it is in a cancellable state.

        Only orders with status 'pending' or 'confirmed' can be
        cancelled. Orders that have already shipped or been delivered
        must be handled through the returns process instead.

        Args:
            order_id: The order's UUID string.
            user_id: The requesting user's identifier.

        Returns:
            Updated order dict with status 'cancelled', or None if
            the order was not found or does not belong to the user.

        Raises:
            ValueError: If the order status does not permit cancellation.
        """
        order = _ORDERS.get(order_id)
        if order is None or order["user_id"] != user_id:
            return None

        if order["status"] not in CANCELLABLE_STATUSES:
            raise ValueError(
                f"Order {order_id} cannot be cancelled: "
                f"status is '{order['status']}'"
            )

        order["status"] = "cancelled"
        order["cancelled_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("Order %s cancelled by user %s", order_id, user_id)
        return order
