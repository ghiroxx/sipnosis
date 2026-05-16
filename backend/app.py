import os

from flask import Flask
from flask_cors import CORS

from routes.health import health_routes
from routes.oracle import oracle_routes

app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

app.register_blueprint(health_routes)
app.register_blueprint(oracle_routes)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
