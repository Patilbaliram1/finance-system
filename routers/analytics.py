from flask import Blueprint, jsonify
from collections import defaultdict
from database import get_db
from auth import login_required
import models

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/summary", methods=["GET"])
@login_required
def get_summary(current_user):
    """
    Get full financial summary.
    - Admins see all transactions.
    - Others see only their own.
    """
    db = get_db()
    try:
        query = db.query(models.Transaction)
        if current_user.role.value != "admin":
            query = query.filter(models.Transaction.user_id == current_user.id)

        transactions = query.all()

        total_income = sum(t.amount for t in transactions if t.type == "income")
        total_expense = sum(t.amount for t in transactions if t.type == "expense")
        current_balance = total_income - total_expense

        # Category breakdown
        cat_map = defaultdict(lambda: {"total": 0.0, "count": 0})
        for t in transactions:
            cat_map[t.category]["total"] += t.amount
            cat_map[t.category]["count"] += 1

        category_breakdown = [
            {"category": cat, "total": round(vals["total"], 2), "count": vals["count"]}
            for cat, vals in sorted(cat_map.items(), key=lambda x: x[1]["total"], reverse=True)
        ]

        # Monthly totals
        monthly_map = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
        for t in transactions:
            key = (t.date.year, t.date.month)
            monthly_map[key][t.type] += t.amount

        monthly_totals = [
            {
                "year": year,
                "month": month,
                "income": round(vals["income"], 2),
                "expense": round(vals["expense"], 2),
                "balance": round(vals["income"] - vals["expense"], 2),
            }
            for (year, month), vals in sorted(monthly_map.items())
        ]

        # Recent 5 transactions
        recent = query.order_by(models.Transaction.date.desc()).limit(5).all()

        return jsonify({
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "current_balance": round(current_balance, 2),
            "total_transactions": len(transactions),
            "category_breakdown": category_breakdown,
            "monthly_totals": monthly_totals,
            "recent_transactions": [t.to_dict() for t in recent],
        }), 200
    finally:
        db.close()
