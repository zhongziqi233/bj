from flask import Flask, jsonify

from .config import Config, ensure_database_directory
from .extensions import cors, db, jwt, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    ensure_database_directory(app.config["SQLALCHEMY_DATABASE_URI"])
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
    )

    from . import models  # noqa: F401
    from .routes import auth_bp, bullet_style_bp, collections_bp, entries_bp, users_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(entries_bp, url_prefix="/api/entries")
    app.register_blueprint(collections_bp, url_prefix="/api/collections")
    app.register_blueprint(bullet_style_bp, url_prefix="/api/bullet-style")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"message": "资源不存在"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"message": "请求方法不允许"}), 405

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"message": "请先登录", "detail": reason}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"message": "登录凭证无效", "detail": reason}), 401

    @jwt.expired_token_loader
    def expired_token(_jwt_header, _jwt_payload):
        return jsonify({"message": "登录已过期，请重新登录"}), 401

    from .cli import ensure_default_admin, register_commands

    register_commands(app)

    if app.config.get("AUTO_CREATE_TABLES"):
        with app.app_context():
            db.create_all()
            ensure_default_admin()

    return app
