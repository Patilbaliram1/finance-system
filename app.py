from flask import Flask, jsonify
from database import engine
import models
from routers.users import users_bp
from routers.transactions import transactions_bp
from routers.analytics import analytics_bp

# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Register Blueprints
app.register_blueprint(users_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(analytics_bp)


@app.route("/")
def root():
    return jsonify({
        "message": "Finance Tracking System API is running",
        "framework": "Flask",
        "endpoints": {
            "users": "/users/register, /users/login, /users/me",
            "transactions": "/transactions/ (GET, POST, PUT, DELETE)",
            "analytics": "/analytics/summary",
        }
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
