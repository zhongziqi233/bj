from flask import Blueprint, g, jsonify, request
from flask_jwt_extended import create_access_token
from sqlalchemy import or_

from ..extensions import db
from ..models import User
from ..utils import (
    login_required,
    validate_email,
    validate_password,
    validate_username,
)

auth_bp = Blueprint("auth", __name__)


def _issue_token(user):
    return create_access_token(identity=str(user.id))


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    error = validate_username(username) or validate_email(email) or validate_password(password)
    if error:
        return jsonify({"message": error}), 400

    if User.query.filter(or_(User.username == username, User.email == email)).first():
        return jsonify({"message": "用户名或邮箱已被注册"}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "注册成功",
                "access_token": _issue_token(user),
                "user": user.to_dict(),
            }
        ),
        201,
    )


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    identifier = (data.get("identifier") or data.get("username") or "").strip()
    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({"message": "请输入用户名/邮箱和密码"}), 400

    user = User.query.filter(
        or_(User.username == identifier, User.email == identifier.lower())
    ).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "用户名或密码错误"}), 401
    if not user.is_active:
        return jsonify({"message": "账号已被禁用，请联系管理员"}), 403

    return jsonify(
        {
            "message": "登录成功",
            "access_token": _issue_token(user),
            "user": user.to_dict(),
        }
    )


@auth_bp.get("/me")
@login_required()
def me():
    return jsonify({"user": g.current_user.to_dict()})


@auth_bp.put("/password")
@login_required()
def change_password():
    data = request.get_json(silent=True) or {}
    old_password = data.get("old_password") or ""
    new_password = data.get("new_password") or ""

    if not g.current_user.check_password(old_password):
        return jsonify({"message": "原密码不正确"}), 400

    error = validate_password(new_password)
    if error:
        return jsonify({"message": error}), 400

    g.current_user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "密码修改成功"})
