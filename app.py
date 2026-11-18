
from flask import Flask, jsonify
from pymongo.errors import PyMongoError

from vulnerabilities.vulnerabilities import vulnerabilities_bp
from auth.auth import auth_bp
from globals import client

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(vulnerabilities_bp)
app.register_blueprint(auth_bp)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the CyberShield Vulnerability Management API",
        "status": "running"
    }), 200


@app.route("/api/v1/health", methods=["GET"])
def health_check():
    try:
        client.admin.command("ping")
        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200

    except PyMongoError:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected"
        }), 503


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
