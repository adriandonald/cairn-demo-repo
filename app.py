"""Order processing API.

Entry point for the demo service. Wires together the auth, order,
and health layers and exposes them via Flask routes.
"""

import logging
import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from services.auth import require_auth
from services.orders import OrderService

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

_order_service = OrderService()


@app.route("/health")
def health() -> Any:
    """Return service health status."""
    return jsonify({"status": "ok", "service": "order-api"})


@app.route("/orders", methods=["GET"])
@require_auth
def list_orders() -> Any:
    """Return orders for the authenticated user.

    Returns:
        JSON list of order records.
    """
    user_id = request.user_id  # type: ignore[attr-defined]
    logger.info("Listing orders for user %s", user_id)
    orders = _order_service.get_orders_for_user(user_id)
    return jsonify(orders)


@app.route("/orders/<int:order_id>", methods=["GET"])
@require_auth
def get_order(order_id: int) -> Any:
    """Return a single order by ID.

    Args:
        order_id: The integer order identifier.

    Returns:
        JSON order record, or 404 if not found.
    """
    user_id = request.user_id  # type: ignore[attr-defined]
    order = _order_service.get_order(order_id, user_id)
    if order is None:
        logger.warning("Order %d not found for user %s", order_id, user_id)
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order)


@app.route("/orders", methods=["POST"])
@require_auth
def create_order() -> Any:
    """Create a new order.

    Request body (JSON):
        items: list of {product_id, quantity} dicts (required).
        shipping_address: string (required).

    Returns:
        JSON record of the created order with HTTP 201.
    """
    user_id = request.user_id  # type: ignore[attr-defined]
    body = request.get_json(silent=True) or {}

    if not body.get("items") or not body.get("shipping_address"):
        return jsonify({"error": "items and shipping_address are required"}), 400

    order = _order_service.create_order(
        user_id=user_id,
        items=body["items"],
        shipping_address=body["shipping_address"],
    )
    logger.info("Created order %s for user %s", order["id"], user_id)
    return jsonify(order), 201


if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", "5001")))
