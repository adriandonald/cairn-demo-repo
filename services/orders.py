"""Order service.

Handles business logic for creating, retrieving, and managing orders.
In this demo the store is an in-memory dict; a real implementation
would use the database layer in db/.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# In-memory store for demo purposes
_ORDERS: dict[str, dict[str, Any]] = {}


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
