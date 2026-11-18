
from flask import Blueprint, jsonify, request, current_app
import json
from bson import json_util
from pymongo.errors import PyMongoError
from decorators import jwt_required
from globals import vulnerabilities
vulnerabilities_bp = Blueprint("vulnerabilities", __name__)

@vulnerabilities_bp.route("/api/v1/vulnerabilities/count", methods=["GET"])
@jwt_required
def vulnerability_count():
    try:
        total = vulnerabilities.count_documents({})
        return jsonify({
            "total_vulnerabilities": total
        }), 200

    except PyMongoError:
        current_app.logger.exception("Error counting vulnerabilities")
        return jsonify({
            "error": "Database error"
        }), 500

@vulnerabilities_bp.route("/api/v1/vulnerabilities", methods=["GET"])
@jwt_required
def get_vulnerabilities():
    # Validate pagination
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return jsonify({
            "error": "page and per_page must be integers"
        }), 400

    if page < 1:
        return jsonify({
            "error": "page must be at least 1"
        }), 400

    if per_page < 1 or per_page > 100:
        return jsonify({
            "error": "per_page must be between 1 and 100"
        }), 400

    # Build database filters
    query = {}

    cve_id = request.args.get("cve_id")
    if cve_id:
        query["cve.id"] = cve_id.strip().upper()

    # Filter by severity using the CVSS v3.1 primary metric
    severity = request.args.get("severity")

    if severity:
        severity = severity.strip().upper()

        allowed_severities = {
            "CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE"
        }

        if severity not in allowed_severities:
            return jsonify({
                "error": "severity must be CRITICAL, HIGH, MEDIUM, LOW, or NONE"
            }), 400

        query["cve.metrics.cvssMetricV31"] = {
            "$elemMatch": {
                "type": "Primary",
                "cvssData.baseSeverity": severity
            }
        }

    # Filter by vulnerability status independently
    status = request.args.get("status")
    if status:
        status = status.strip().upper()
        allowed_statuses = {"PUBLISHED", "REJECTED"}

        if status not in allowed_statuses:
            return jsonify({
                "error": "status must be PUBLISHED or REJECTED"
            }), 400

        query["cve.vulnStatus"] = status

    # Query MongoDB
    try:
        total = vulnerabilities.count_documents(query)

        cursor = (
            vulnerabilities.find(query, {"_id": 0})
            .sort("cve.id", 1)
            .skip((page - 1) * per_page)
            .limit(per_page)
        )

        records = list(cursor)
        records = json.loads(json_util.dumps(records))

        return jsonify({
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
            "vulnerabilities": records
        }), 200

    except PyMongoError:
        current_app.logger.exception("Failed to retrieve vulnerabilities")
        return jsonify({
            "error": "Unable to retrieve vulnerabilities"
        }), 500
    
@vulnerabilities_bp.route("/api/v1/vulnerabilities", methods=["POST"])
@jwt_required
def create_vulnerability():
    # Read form fields from Postman
    cve_id = request.form.get("cve_id", "").strip().upper()
    vendor = request.form.get("vendor", "").strip()
    product = request.form.get("product", "").strip()
    description = request.form.get("description", "").strip()

    # Validate required fields
    if not cve_id or not vendor or not product or not description:
        return jsonify({
            "error": "cve_id, vendor, product, and description are required"
        }), 400

    # Protect the imported NVD records during testing
    if not cve_id.startswith("CVE-TEST-"):
        return jsonify({
            "error": "For now, use a test ID starting with CVE-TEST-"
        }), 400

    # Build a document in the NVD-style structure
    document = {
        "cve": {
            "id": cve_id,
            "sourceIdentifier": "cybershield-test",
            "vulnStatus": "Under Review",
            "descriptions": [
                {
                    "lang": "en",
                    "value": description
                }
            ],
            "affected": [
                {
                    "vendor": vendor,
                    "product": product
                }
            ]
        },
        "_managed_by": "cybershield_api_test"
    }

    try:
        if vulnerabilities.find_one({"cve.id": cve_id}):
            return jsonify({
                "error": "A vulnerability with this CVE ID already exists"
            }), 409

        result = vulnerabilities.insert_one(document)

        return jsonify({
            "message": "Test vulnerability created successfully",
            "id": str(result.inserted_id),
            "cve_id": cve_id
        }), 201

    except PyMongoError:
        current_app.logger.exception("Failed to create test vulnerability")
        return jsonify({
            "error": "Unable to create vulnerability"
        }), 500
    
@vulnerabilities_bp.route("/api/v1/vulnerabilities/<cve_id>", methods=["PUT"])
@jwt_required
def update_vulnerability(cve_id):
    cve_id = cve_id.strip().upper()

    vendor = request.form.get("vendor", "").strip()
    product = request.form.get("product", "").strip()
    description = request.form.get("description", "").strip()

    if not vendor or not product or not description:
        return jsonify({
            "error": "vendor, product, and description are required"
        }), 400

    try:
        result = vulnerabilities.update_one(
            {
                "cve.id": cve_id,
                "_managed_by": "cybershield_api_test"
            },
            {
                "$set": {
                    "cve.affected": [{
                        "vendor": vendor,
                        "product": product
                    }],
                    "cve.descriptions": [{
                        "lang": "en",
                        "value": description
                    }]
                }
            }
        )

        if result.matched_count == 0:
            return jsonify({
                "error": "Test vulnerability not found"
            }), 404

        return jsonify({
            "message": "Test vulnerability updated successfully",
            "cve_id": cve_id
        }), 200

    except PyMongoError:
        current_app.logger.exception("Failed to update test vulnerability")
        return jsonify({
            "error": "Unable to update vulnerability"
        }), 500
    
@vulnerabilities_bp.route("/api/v1/vulnerabilities/<cve_id>", methods=["DELETE"])
@jwt_required
def delete_vulnerability(cve_id):
    cve_id = cve_id.strip().upper()

    try:
        result = vulnerabilities.delete_one({
            "cve.id": cve_id,
            "_managed_by": "cybershield_api_test"
        })

        if result.deleted_count == 0:
            return jsonify({
                "error": "Test vulnerability not found"
            }), 404

        return jsonify({
            "message": "Test vulnerability deleted successfully",
            "cve_id": cve_id
        }), 200

    except PyMongoError:
        current_app.logger.exception("Failed to delete test vulnerability")
        return jsonify({
            "error": "Unable to delete vulnerability"
        }), 500