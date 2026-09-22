from flask import Blueprint, g, jsonify, request

from ..extensions import db
from ..models import Collection
from ..utils import login_required

collections_bp = Blueprint("collections", __name__)


def _get_owned_collection(collection_id):
    return Collection.query.filter_by(
        id=collection_id,
        user_id=g.current_user.id,
    ).first()


@collections_bp.get("")
@login_required()
def list_collections():
    collections = (
        Collection.query.filter_by(user_id=g.current_user.id)
        .order_by(Collection.updated_at.desc())
        .all()
    )
    return jsonify({"items": [item.to_dict() for item in collections]})


@collections_bp.post("")
@login_required()
def create_collection():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip()
    if not name or len(name) > 100:
        return jsonify({"message": "集合名称长度需为 1-100 个字符"}), 400
    if len(description) > 500:
        return jsonify({"message": "集合描述不能超过 500 个字符"}), 400

    collection = Collection(
        user_id=g.current_user.id,
        name=name,
        description=description,
    )
    db.session.add(collection)
    db.session.commit()
    return jsonify({"message": "集合已创建", "collection": collection.to_dict()}), 201


@collections_bp.get("/<int:collection_id>")
@login_required()
def get_collection(collection_id):
    collection = _get_owned_collection(collection_id)
    if not collection:
        return jsonify({"message": "集合不存在"}), 404
    return jsonify({"collection": collection.to_dict(include_entries=True)})


@collections_bp.patch("/<int:collection_id>")
@login_required()
def update_collection(collection_id):
    collection = _get_owned_collection(collection_id)
    if not collection:
        return jsonify({"message": "集合不存在"}), 404

    data = request.get_json(silent=True) or {}
    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name or len(name) > 100:
            return jsonify({"message": "集合名称长度需为 1-100 个字符"}), 400
        collection.name = name
    if "description" in data:
        description = (data.get("description") or "").strip()
        if len(description) > 500:
            return jsonify({"message": "集合描述不能超过 500 个字符"}), 400
        collection.description = description

    db.session.commit()
    return jsonify({"message": "集合已更新", "collection": collection.to_dict()})


@collections_bp.delete("/<int:collection_id>")
@login_required()
def delete_collection(collection_id):
    collection = _get_owned_collection(collection_id)
    if not collection:
        return jsonify({"message": "集合不存在"}), 404

    db.session.delete(collection)
    db.session.commit()
    return jsonify({"message": "集合已删除"})

