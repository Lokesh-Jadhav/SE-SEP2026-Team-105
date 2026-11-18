import datetime
import jwt
from flask import request, jsonify, current_app
from functools import wraps
from app.models import User


def create_token(user):
    payload = {
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=current_app.config["JWT_EXPIRY_HOURS"]),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])


def get_current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None

    try:
        payload = decode_token(auth.split(" ", 1)[1])
    except Exception:
        return None

    return User.query.get(payload.get("user_id"))


def login_required(roles=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({"error": "Authentication required"}), 401

            if roles and user.role not in roles:
                return jsonify({"error": "Unauthorized"}), 403

            return fn(user, *args, **kwargs)

        return wrapper

    return decorator