from flask import Flask, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from database import engine
import models
from routers.users import users_bp
from routers.transactions import transactions_bp
from routers.analytics import analytics_bp

# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
CORS(app)

# Register Blueprints
app.register_blueprint(users_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(analytics_bp)

# Swagger UI setup
SWAGGER_URL = "/docs"
API_URL = "/openapi.json"
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint)


@app.route("/openapi.json")
def openapi_spec():
    return jsonify({
        "openapi": "3.0.0",
        "info": {"title": "Finance Tracking System", "version": "1.0.0",
                 "description": "A Python-based backend for managing personal financial records, summaries, and analytics."},
        "components": {
            "securitySchemes": {
                "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            },
            "schemas": {
                "UserRegister": {
                    "type": "object",
                    "required": ["username", "email", "password"],
                    "properties": {
                        "username": {"type": "string", "example": "john"},
                        "email": {"type": "string", "example": "john@example.com"},
                        "password": {"type": "string", "example": "pass123"},
                        "role": {"type": "string", "enum": ["viewer", "analyst", "admin"], "example": "analyst"}
                    }
                },
                "UserLogin": {
                    "type": "object",
                    "required": ["username", "password"],
                    "properties": {
                        "username": {"type": "string", "example": "admin"},
                        "password": {"type": "string", "example": "admin123"}
                    }
                },
                "TransactionCreate": {
                    "type": "object",
                    "required": ["amount", "type", "category", "date"],
                    "properties": {
                        "amount": {"type": "number", "example": 5000},
                        "type": {"type": "string", "enum": ["income", "expense"], "example": "income"},
                        "category": {"type": "string", "example": "Salary"},
                        "date": {"type": "string", "format": "date", "example": "2025-04-01"},
                        "notes": {"type": "string", "example": "Monthly salary"}
                    }
                },
                "TransactionUpdate": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number", "example": 6000},
                        "type": {"type": "string", "enum": ["income", "expense"]},
                        "category": {"type": "string", "example": "Freelance"},
                        "date": {"type": "string", "format": "date"},
                        "notes": {"type": "string"}
                    }
                }
            }
        },
        "security": [{"BearerAuth": []}],
        "paths": {
            "/users/register": {"post": {"tags": ["Users"], "summary": "Register a new user", "security": [],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserRegister"}}}},
                "responses": {"201": {"description": "User created"}, "400": {"description": "Validation error"}}}},
            "/users/login": {"post": {"tags": ["Users"], "summary": "Login and get JWT token", "security": [],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserLogin"}}}},
                "responses": {"200": {"description": "Returns access_token"}, "401": {"description": "Invalid credentials"}}}},
            "/users/me": {"get": {"tags": ["Users"], "summary": "Get current user profile",
                "responses": {"200": {"description": "User profile"}, "401": {"description": "Unauthorized"}}}},
            "/users/": {"get": {"tags": ["Users"], "summary": "List all users (Admin only)",
                "responses": {"200": {"description": "List of users"}, "403": {"description": "Forbidden"}}}},
            "/users/{user_id}": {"delete": {"tags": ["Users"], "summary": "Delete a user (Admin only)",
                "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Deleted"}, "404": {"description": "Not found"}}}},
            "/transactions/": {
                "get": {"tags": ["Transactions"], "summary": "List transactions with filters",
                    "parameters": [
                        {"name": "type", "in": "query", "schema": {"type": "string", "enum": ["income", "expense"]}},
                        {"name": "category", "in": "query", "schema": {"type": "string"}},
                        {"name": "start_date", "in": "query", "schema": {"type": "string", "format": "date"}},
                        {"name": "end_date", "in": "query", "schema": {"type": "string", "format": "date"}},
                        {"name": "skip", "in": "query", "schema": {"type": "integer", "default": 0}},
                        {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 50}}
                    ],
                    "responses": {"200": {"description": "List of transactions"}}},
                "post": {"tags": ["Transactions"], "summary": "Create a new transaction (Analyst/Admin)",
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/TransactionCreate"}}}},
                    "responses": {"201": {"description": "Transaction created"}, "403": {"description": "Forbidden"}}}
            },
            "/transactions/{tx_id}": {
                "get": {"tags": ["Transactions"], "summary": "Get a single transaction",
                    "parameters": [{"name": "tx_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "Transaction"}, "404": {"description": "Not found"}}},
                "put": {"tags": ["Transactions"], "summary": "Update a transaction (Analyst/Admin)",
                    "parameters": [{"name": "tx_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/TransactionUpdate"}}}},
                    "responses": {"200": {"description": "Updated"}, "404": {"description": "Not found"}}},
                "delete": {"tags": ["Transactions"], "summary": "Delete a transaction (Admin only)",
                    "parameters": [{"name": "tx_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "Deleted"}, "404": {"description": "Not found"}}}
            },
            "/analytics/summary": {"get": {"tags": ["Analytics"], "summary": "Get full financial summary",
                "responses": {"200": {"description": "Summary with income, expenses, balance, categories, monthly totals"}}}}
        }
    })


@app.route("/")
def root():
    return jsonify({
        "message": "Finance Tracking System API is running",
        "framework": "Flask",
        "docs": "http://127.0.0.1:5000/docs",
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
    app.run(debug=True, port=5000)
