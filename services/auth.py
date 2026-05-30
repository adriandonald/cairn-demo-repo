"""Authentication service.

Handles JWT token validation and the require_auth decorator used
by all protected API endpoints. Tokens are signed with HS256 using
the SECRET_KEY environment variable.
"""

import logging
import os
from functools import wraps
from typing import Any, Callable

import jwt
from flask import jsonify, request

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"
TOKEN_PREFIX = "Bearer "


def require_auth(f: Callable) -> Callable:
    """Decorator that validates a JWT bearer token on the request.

    Reads the Authorization header, validates the token, and attaches
    the decoded user_id to the request object. Returns 401 if the
    token is missing, expired, or invalid.

    Args:
        f: The route function to protect.

    Returns:
        Wrapped function with auth enforcement.
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith(TOKEN_PREFIX):
            logger.warning("Missing or malformed Authorization header")
            return jsonify({"error": "Authorization header required"}), 401

        token = auth_header[len(TOKEN_PREFIX):]
        payload = _validate_token(token)
        if payload is None:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.user_id = payload["sub"]  # type: ignore[attr-defined]
        return f(*args, **kwargs)

    return decorated


def _validate_token(token: str) -> dict[str, Any] | None:
    """Validate a JWT token and return its payload.

    Args:
        token: Raw JWT string.

    Returns:
        Decoded payload dict, or None if validation fails.
    """
    secret = os.getenv("SECRET_KEY")
    if not secret:
        logger.error("SECRET_KEY environment variable is not set")
        return None

    try:
        return jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as exc:
        logger.warning("Token validation failed: %s", exc)
        return None
