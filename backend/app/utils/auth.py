from functools import wraps

from flask import g, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from ..extensions import db
from ..models import User


def get_current_user():
    identity = get_jwt_identity()
    if identity is None:
        return None
    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return None
    return db.session.get(User, user_id)


def login_required(admin=False):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            if not user:
                return jsonify({"message": "用户不存在"}), 401
            if not user.is_active:
                return jsonify({"message": "账号已被禁用，请联系管理员"}), 403
            if admin and not user.is_admin:
                return jsonify({"message": "需要管理员权限"}), 403
            g.current_user = user
            return view(*args, **kwargs)

        return wrapped

    return decorator

