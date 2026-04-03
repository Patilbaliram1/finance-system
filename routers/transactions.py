from flask import Blueprint, request, jsonify
from datetime import datetime
from database import get_db
from auth import login_required, role_required
import models

transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions")


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def get_transactions_query(db, user_id, role):
    query = db.query(models.Transaction)
    if role != "admin":
        query = query.filter(models.Transaction.user_id == user_id)
    return query


@transactions_bp.route("/", methods=["POST"])
@role_required("admin", "analyst")
def create_transaction(current_user):
    """Create a new transaction. Analyst and Admin only."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Validation
    amount = data.get("amount")
    tx_type = data.get("type", "")
    category = data.get("category", "").strip()
    date_str = data.get("date", "")
    notes = data.get("notes", None)

    if amount is None or not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "Amount must be a positive number"}), 400
    if tx_type not in ["income", "expense"]:
        return jsonify({"error": "Type must be 'income' or 'expense'"}), 400
    if not category:
        return jsonify({"error": "Category is required"}), 400

    tx_date = parse_date(date_str)
    if not tx_date:
        return jsonify({"error": "Date must be in YYYY-MM-DD format"}), 400

    db = get_db()
    try:
        tx = models.Transaction(
            amount=amount,
            type=tx_type,
            category=category,
            date=tx_date,
            notes=notes,
            user_id=current_user.id,
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return jsonify(tx.to_dict()), 201
    finally:
        db.close()


@transactions_bp.route("/", methods=["GET"])
@login_required
def list_transactions(current_user):
    """List transactions with optional filters. All roles allowed."""
    tx_type = request.args.get("type")
    category = request.args.get("category")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    skip = int(request.args.get("skip", 0))
    limit = min(int(request.args.get("limit", 50)), 200)

    # Validate date filters
    if start_date:
        start_date = parse_date(start_date)
        if not start_date:
            return jsonify({"error": "start_date must be YYYY-MM-DD"}), 400
    if end_date:
        end_date = parse_date(end_date)
        if not end_date:
            return jsonify({"error": "end_date must be YYYY-MM-DD"}), 400
    if start_date and end_date and start_date > end_date:
        return jsonify({"error": "start_date must be before end_date"}), 400
    if tx_type and tx_type not in ["income", "expense"]:
        return jsonify({"error": "type must be 'income' or 'expense'"}), 400

    db = get_db()
    try:
        query = get_transactions_query(db, current_user.id, current_user.role.value)

        if tx_type:
            query = query.filter(models.Transaction.type == tx_type)
        if category:
            query = query.filter(models.Transaction.category.ilike(f"%{category}%"))
        if start_date:
            query = query.filter(models.Transaction.date >= start_date)
        if end_date:
            query = query.filter(models.Transaction.date <= end_date)

        transactions = query.order_by(models.Transaction.date.desc()).offset(skip).limit(limit).all()
        return jsonify([t.to_dict() for t in transactions]), 200
    finally:
        db.close()


@transactions_bp.route("/<int:tx_id>", methods=["GET"])
@login_required
def get_transaction(current_user, tx_id):
    """Get a single transaction by ID."""
    db = get_db()
    try:
        query = get_transactions_query(db, current_user.id, current_user.role.value)
        tx = query.filter(models.Transaction.id == tx_id).first()
        if not tx:
            return jsonify({"error": "Transaction not found"}), 404
        return jsonify(tx.to_dict()), 200
    finally:
        db.close()


@transactions_bp.route("/<int:tx_id>", methods=["PUT"])
@role_required("admin", "analyst")
def update_transaction(current_user, tx_id):
    """Update a transaction. Analyst and Admin only."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    db = get_db()
    try:
        query = get_transactions_query(db, current_user.id, current_user.role.value)
        tx = query.filter(models.Transaction.id == tx_id).first()
        if not tx:
            return jsonify({"error": "Transaction not found"}), 404

        if "amount" in data:
            if not isinstance(data["amount"], (int, float)) or data["amount"] <= 0:
                return jsonify({"error": "Amount must be a positive number"}), 400
            tx.amount = data["amount"]
        if "type" in data:
            if data["type"] not in ["income", "expense"]:
                return jsonify({"error": "Type must be 'income' or 'expense'"}), 400
            tx.type = data["type"]
        if "category" in data:
            tx.category = data["category"]
        if "date" in data:
            parsed = parse_date(data["date"])
            if not parsed:
                return jsonify({"error": "Date must be YYYY-MM-DD"}), 400
            tx.date = parsed
        if "notes" in data:
            tx.notes = data["notes"]

        db.commit()
        db.refresh(tx)
        return jsonify(tx.to_dict()), 200
    finally:
        db.close()


@transactions_bp.route("/<int:tx_id>", methods=["DELETE"])
@role_required("admin")
def delete_transaction(current_user, tx_id):
    """Delete a transaction. Admin only."""
    db = get_db()
    try:
        tx = db.query(models.Transaction).filter(models.Transaction.id == tx_id).first()
        if not tx:
            return jsonify({"error": "Transaction not found"}), 404
        db.delete(tx)
        db.commit()
        return jsonify({"message": "Transaction deleted successfully"}), 200
    finally:
        db.close()
