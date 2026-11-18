
from flask import Blueprint, jsonify, request, g
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from globals import users, secret_key
from decorators import jwt_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/v1/auth/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "")

    if not username or not password:
        return jsonify({
            "error": "Username and password are required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters long"
        }), 400

    if users.find_one({"username": username}):
        return jsonify({
            "error": "Username already exists"
        }), 409

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    users.insert_one({
        "username": username,
        "password_hash": password_hash,
        "role": "user"
    })

    return jsonify({
        "message": "User registered successfully",
        "username": username
    }), 201


@auth_bp.route("/api/v1/auth/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "")

    user = users.find_one({"username": username})

    if not user or not bcrypt.checkpw(
        password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    ):
        return jsonify({"error": "Invalid username or password"}), 401
        
    access_token = jwt.encode(
        {
            "user_id": str(user["_id"]),
            "username": user["username"],
            "role": user.get("role", "user"),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        },
        secret_key,
        algorithm="HS256"
    )

    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer"
    }), 200


@auth_bp.route("/api/v1/auth/me", methods=["GET"])
@jwt_required
def get_current_user():
    user = g.current_user

    return jsonify({
        "message": "Basic authentication successful",
        "user_id": str(user["_id"]),
        "username": user["username"],
        "role": user.get("role", "user")
    }), 200
