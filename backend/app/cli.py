import click
from flask import Flask, current_app

from .extensions import db
from .models import User


def ensure_default_admin():
    username = current_app.config.get("DEFAULT_ADMIN_USERNAME", "admin")
    email = current_app.config.get("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    password = current_app.config.get("DEFAULT_ADMIN_PASSWORD", "Admin123456")

    existing = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing:
        return existing

    admin = User(
        username=username,
        email=email,
        is_admin=True,
        is_active=True,
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Default admin created: {username}")
    return admin


def register_commands(app: Flask):
    @app.cli.command("init-db")
    def init_db_command():
        """Create database tables and the default administrator."""
        db.create_all()
        ensure_default_admin()
        click.echo("Database initialized.")


__all__ = ["ensure_default_admin", "register_commands"]
