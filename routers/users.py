from flask import Blueprint, request, jsonify
from database import get_db
from auth import hash_password, verify_password, create_access_token, login_required, role_required
import models

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/register", methods=["POST"])
def register():
    """Register a new user. Default role is 'viewer'."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    role = data.get("role", "viewer")

    # Validation
    if not username or len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if not email or "@" not in email:
        return jsonify({"error": "Valid email is required"}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if role not in ["viewer", "analyst", "admin"]:
        return jsonify({"error": "Role must be viewer, analyst, or admin"}), 400

    db = get_db()
    try:
        if db.query(models.User).filter(models.User.username == username).first():
            return jsonify({"error": "Username already taken"}), 400
        if db.query(models.User).filter(models.User.email == email).first():
            return jsonify({"error": "Email already registered"}), 400

        user = models.User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return jsonify(user.to_dict()), 201
    finally:
        db.close()


@users_bp.route("/login", methods=["POST"])
def login():
    """Login and receive a JWT access token."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    db = get_db()
    try:
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return jsonify({"error": "Incorrect username or password"}), 401

        token = create_access_token({"sub": user.username})
        return jsonify({"access_token": token, "token_type": "bearer"}), 200
    finally:
        db.close()


@users_bp.route("/me", methods=["GET"])
@login_required
def get_me(current_user):
    """Get the currently authenticated user's profile."""
    return jsonify(current_user.to_dict()), 200


@users_bp.route("/", methods=["GET"])
@role_required("admin")
def list_users(current_user):
    """List all users. Admin only."""
    db = get_db()
    try:
        users = db.query(models.User).all()
        return jsonify([u.to_dict() for u in users]), 200
    finally:
        db.close()


@users_bp.route("/<int:user_id>", methods=["DELETE"])
@role_required("admin")
def delete_user(current_user, user_id):
    """Delete a user by ID. Admin only."""
    if current_user.id == user_id:
        return jsonify({"error": "Cannot delete your own account"}), 400

    db = get_db()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        db.delete(user)
        db.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    finally:
        db.close()
