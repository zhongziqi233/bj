from flask import Blueprint, g, jsonify, request
from sqlalchemy import or_

from ..extensions import db
from ..models import User
from ..utils import login_required, parse_bool, validate_password

users_bp = Blueprint("users", __name__)


def _admin_count():
    return User.query.filter_by(is_admin=True).count()


@users_bp.get("")
@login_required(admin=True)
def list_users():
    page = max(request.args.get("page", 1, type=int), 1)
    page_size = min(max(request.args.get("page_size", 20, type=int), 1), 100)
    search = (request.args.get("search") or "").strip()

    query = User.query
    if search:
        like = f"%{search}%"
        query = query.filter(or_(User.username.like(like), User.email.like(like)))

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=page_size,
        error_out=False,
    )
    return jsonify(
        {
            "items": [user.to_dict() for user in pagination.items],
            "total": pagination.total,
            "page": pagination.page,
            "page_size": pagination.per_page,
            "pages": pagination.pages,
        }
    )


@users_bp.patch("/<int:user_id>")
@login_required(admin=True)
def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "用户不存在"}), 404

    data = request.get_json(silent=True) or {}
    changing_admin = "is_admin" in data
    changing_active = "is_active" in data
    next_admin = parse_bool(data.get("is_admin"), user.is_admin) if changing_admin else user.is_admin
    next_active = parse_bool(data.get("is_active"), user.is_active) if changing_active else user.is_active

    if user.id == g.current_user.id and (not next_admin or not next_active):
        return jsonify({"message": "不能取消自己的管理员权限或禁用自己"}), 400

    if user.is_admin and not next_admin and _admin_count() <= 1:
        return jsonify({"message": "系统至少需要保留一名管理员"}), 400

    user.is_admin = next_admin
    user.is_active = next_active
    db.session.commit()
    return jsonify({"message": "用户信息已更新", "user": user.to_dict()})


@users_bp.post("/<int:user_id>/reset-password")
@login_required(admin=True)
def reset_password(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "用户不存在"}), 404

    data = request.get_json(silent=True) or {}
    new_password = data.get("new_password") or ""
    error = validate_password(new_password)
    if error:
        return jsonify({"message": error}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "密码已重置"})


@users_bp.delete("/<int:user_id>")
@login_required(admin=True)
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "用户不存在"}), 404
    if user.id == g.current_user.id:
        return jsonify({"message": "不能删除自己的账号"}), 400
    if user.is_admin and _admin_count() <= 1:
        return jsonify({"message": "系统至少需要保留一名管理员"}), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "用户已删除"})

