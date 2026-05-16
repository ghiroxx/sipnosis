from flask import Blueprint, jsonify

health_routes = Blueprint("health_routes", __name__)


@health_routes.route("/health", methods=["GET"])
def healthcheck():
    return jsonify(
        {
            "status": "ok",
            "service": "sipnosis-backend",
            "version": "phase-1-routes",
        }
    )


@health_routes.route("/ping", methods=["GET"])
def ping():
    return jsonify(
        {
            "status": "ok",
            "service": "sipnosis-backend",
        }
    )
