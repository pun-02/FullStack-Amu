
from functools import wraps
import bcrypt
from flask import request, jsonify, g
from globals import users


def jwt_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return jsonify({"error": "Basic authentication is required"}), 401

        username = auth.username.strip().lower()
        user = users.find_one({"username": username})

        if not user or not bcrypt.checkpw(
            auth.password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        ):
            return jsonify({"error": "Invalid username or password"}), 401

        g.current_user = user

        return f(*args, **kwargs)

    return decorator
