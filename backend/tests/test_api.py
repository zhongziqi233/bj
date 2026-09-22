import os
import copy

import pytest
from sqlalchemy.pool import StaticPool

from app import create_app
from app.config import Config
from app.extensions import db
from app.models import Entry, User


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret-key-with-more-than-32-bytes"
    JWT_SECRET_KEY = "test-jwt-secret-key-with-more-than-32-bytes"
    SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URL or "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = (
        {"pool_pre_ping": True, "pool_recycle": 280}
        if TEST_DATABASE_URL
        else {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    )
    AUTO_CREATE_TABLES = False
    CORS_ORIGINS = "*"


@pytest.fixture()
def app():
    application = create_app(TestConfig)
    with application.app_context():
        if TEST_DATABASE_URL:
            db.drop_all()
        db.create_all()

        admin = User(username="admin", email="admin@example.com", is_admin=True)
        admin.set_password("Admin123456")
        db.session.add(admin)
        db.session.commit()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def auth_headers(client, identifier="admin", password="Admin123456"):
    response = client.post(
        "/api/auth/login",
        json={"identifier": identifier, "password": password},
    )
    assert response.status_code == 200
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123",
        },
    )
    assert response.status_code == 201
    payload = response.get_json()
    assert payload["user"]["username"] == "alice"
    assert payload["access_token"]

    login_response = client.post(
        "/api/auth/login",
        json={"identifier": "alice@example.com", "password": "Password123"},
    )
    assert login_response.status_code == 200


def test_daily_entry_lifecycle_and_migration(client):
    headers = auth_headers(client)

    create_response = client.post(
        "/api/entries",
        headers=headers,
        json={
            "kind": "task",
            "content": "整理本周计划",
            "important": True,
            "log_type": "daily",
            "entry_date": "2026-09-17",
        },
    )
    assert create_response.status_code == 201
    entry = create_response.get_json()["entry"]
    assert entry["status"] == "open"
    assert entry["important"] is True

    migrate_response = client.post(
        f"/api/entries/{entry['id']}/migrate",
        headers=headers,
        json={"target_date": "2026-09-18"},
    )
    assert migrate_response.status_code == 200
    migrated_payload = migrate_response.get_json()
    assert migrated_payload["new_entry"]["entry_date"] == "2026-09-18"
    assert migrated_payload["entry"]["status"] == "migrated"

    complete_response = client.patch(
        f"/api/entries/{migrated_payload['new_entry']['id']}",
        headers=headers,
        json={"status": "completed"},
    )
    assert complete_response.status_code == 200
    assert complete_response.get_json()["entry"]["status"] == "completed"

    list_response = client.get(
        "/api/entries?log_type=daily&date=2026-09-18",
        headers=headers,
    )
    assert list_response.status_code == 200
    assert len(list_response.get_json()["items"]) == 1

    postpone_source = client.post(
        "/api/entries",
        headers=headers,
        json={
            "kind": "task",
            "content": "明天继续处理",
            "log_type": "daily",
            "entry_date": "2026-09-19",
        },
    ).get_json()["entry"]
    postpone_response = client.post(
        f"/api/entries/{postpone_source['id']}/postpone",
        headers=headers,
    )
    assert postpone_response.status_code == 200
    postpone_payload = postpone_response.get_json()
    assert postpone_payload["entry"]["status"] == "postponed"
    assert postpone_payload["new_entry"]["entry_date"] == "2026-09-20"


def test_admin_can_manage_users_and_regular_user_cannot(client):
    headers = auth_headers(client)

    create_response = client.post(
        "/api/auth/register",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "Password123",
        },
    )
    assert create_response.status_code == 201

    users_response = client.get("/api/users", headers=headers)
    assert users_response.status_code == 200
    assert users_response.get_json()["total"] == 2

    bob_headers = auth_headers(client, "bob", "Password123")
    forbidden_response = client.get("/api/users", headers=bob_headers)
    assert forbidden_response.status_code == 403

    bob_id = create_response.get_json()["user"]["id"]
    disable_response = client.patch(
        f"/api/users/{bob_id}",
        headers=headers,
        json={"is_active": False},
    )
    assert disable_response.status_code == 200
    assert disable_response.get_json()["user"]["is_active"] is False


def test_collection_entries_are_scoped_to_owner(client):
    headers = auth_headers(client)

    collection_response = client.post(
        "/api/collections",
        headers=headers,
        json={"name": "阅读清单", "description": "今年想读的书"},
    )
    assert collection_response.status_code == 201
    collection_id = collection_response.get_json()["collection"]["id"]

    entry_response = client.post(
        "/api/entries",
        headers=headers,
        json={
            "kind": "note",
            "content": "读完《人类简史》",
            "log_type": "collection",
            "collection_id": collection_id,
        },
    )
    assert entry_response.status_code == 201
    assert entry_response.get_json()["entry"]["collection_id"] == collection_id

    list_response = client.get(
        f"/api/entries?log_type=collection&collection_id={collection_id}",
        headers=headers,
    )
    assert list_response.status_code == 200
    assert len(list_response.get_json()["items"]) == 1

    with client.application.app_context():
        assert Entry.query.count() == 1


def test_bullet_style_can_be_customized_and_reset(client):
    headers = auth_headers(client)

    initial_response = client.get("/api/bullet-style", headers=headers)
    assert initial_response.status_code == 200
    initial_payload = initial_response.get_json()
    assert initial_payload["is_custom"] is False
    assert initial_payload["config"]["task"]["layers"][0]["shape"] == "dot"

    config = copy.deepcopy(initial_payload["config"])
    config["task"]["layers"][0].update(
        {
            "shape": "star",
            "fill": "#e06c75",
            "stroke": "none",
            "size": 72,
        }
    )

    save_response = client.put(
        "/api/bullet-style",
        headers=headers,
        json={"config": config},
    )
    assert save_response.status_code == 200
    assert save_response.get_json()["is_custom"] is True

    stored_response = client.get("/api/bullet-style", headers=headers)
    assert stored_response.status_code == 200
    stored_payload = stored_response.get_json()
    assert stored_payload["is_custom"] is True
    assert stored_payload["config"]["task"]["layers"][0]["shape"] == "star"

    invalid_config = copy.deepcopy(config)
    invalid_config["task"]["layers"][0].update(
        {"type": "path", "path": "<script>alert(1)</script>"}
    )
    invalid_response = client.put(
        "/api/bullet-style",
        headers=headers,
        json={"config": invalid_config},
    )
    assert invalid_response.status_code == 400

    reset_response = client.delete("/api/bullet-style", headers=headers)
    assert reset_response.status_code == 200
    assert reset_response.get_json()["is_custom"] is False
    assert reset_response.get_json()["config"]["task"]["layers"][0]["shape"] == "dot"
