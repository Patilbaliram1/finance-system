from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify
from jose import JWTError, jwt
import bcrypt
from database import get_db
import models

SECRET_KEY = "finance-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user():
    """Extract and validate JWT token from request headers."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, "Missing or invalid Authorization header"

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None, "Invalid token"
    except JWTError:
        return None, "Invalid or expired token"

    db = get_db()
    user = db.query(models.User).filter(models.User.username == username).first()
    db.close()
    if not user:
        return None, "User not found"
    return user, None


def login_required(f):
    """Decorator: requires valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user, error = get_current_user()
        if error:
            return jsonify({"error": error}), 401
        return f(user, *args, **kwargs)
    return decorated


def role_required(*roles):
    """Decorator: requires valid JWT token AND specific role(s)."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user, error = get_current_user()
            if error:
                return jsonify({"error": error}), 401
            if user.role.value not in roles:
                return jsonify({"error": f"Access denied. Required role(s): {', '.join(roles)}"}), 403
            return f(user, *args, **kwargs)
        return decorated
    return decorator
