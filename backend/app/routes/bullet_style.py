import copy
import re

from flask import Blueprint, g, jsonify, request

from ..extensions import db
from ..models import BulletStyle
from ..utils import login_required

bullet_style_bp = Blueprint("bullet_style", __name__)

KINDS = ("task", "event", "note")
LAYER_TYPES = {"preset", "path", "svg"}
STATUSES = ("completed", "postponed", "migrated", "scheduled")
DEFAULT_CONFIG = {
    "task": {
        "layers": [
            {
                "id": "task-dot",
                "type": "preset",
                "shape": "dot",
                "size": 38,
                "x": 0,
                "y": 0,
                "rotation": 0,
                "opacity": 100,
                "fill": "#e5c07b",
                "stroke": "none",
                "strokeWidth": 1.8,
            }
        ],
        "statuses": {
            "completed": {
                "layers": [
                    {
                        "id": "task-completed",
                        "type": "preset",
                        "shape": "x",
                        "size": 82,
                        "x": 0,
                        "y": 0,
                        "rotation": 0,
                        "opacity": 100,
                        "fill": "none",
                        "stroke": "#98c379",
                        "strokeWidth": 2.1,
                    }
                ]
            },
            "postponed": {
                "layers": [
                    {
                        "id": "task-postponed",
                        "type": "preset",
                        "shape": "gt",
                        "size": 86,
                        "x": 0,
                        "y": 0,
                        "rotation": 0,
                        "opacity": 100,
                        "fill": "none",
                        "stroke": "#e5c07b",
                        "strokeWidth": 2.1,
                    }
                ]
            },
            "migrated": {
                "layers": [
                    {
                        "id": "task-migrated",
                        "type": "preset",
                        "shape": "lt",
                        "size": 86,
                        "x": 0,
                        "y": 0,
                        "rotation": 0,
                        "opacity": 100,
                        "fill": "none",
                        "stroke": "#d19a66",
                        "strokeWidth": 2.1,
                    }
                ]
            },
            "scheduled": {
                "layers": [
                    {
                        "id": "task-scheduled",
                        "type": "preset",
                        "shape": "arrow",
                        "size": 86,
                        "x": 0,
                        "y": 0,
                        "rotation": 0,
                        "opacity": 100,
                        "fill": "none",
                        "stroke": "#61afef",
                        "strokeWidth": 2.1,
                    }
                ]
            },
        },
    },
    "event": {
        "layers": [
            {
                "id": "event-ring",
                "type": "preset",
                "shape": "ring",
                "size": 86,
                "x": 0,
                "y": 0,
                "rotation": 0,
                "opacity": 100,
                "fill": "none",
                "stroke": "#61afef",
                "strokeWidth": 1.9,
            }
        ]
    },
    "note": {
        "layers": [
            {
                "id": "note-line",
                "type": "preset",
                "shape": "line",
                "size": 86,
                "x": 0,
                "y": 0,
                "rotation": 0,
                "opacity": 100,
                "fill": "none",
                "stroke": "#c678dd",
                "strokeWidth": 2.1,
            }
        ]
    },
}

ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
SHAPE_RE = re.compile(r"^[a-z0-9_-]{1,32}$")
PATH_RE = re.compile(r"^[0-9A-Za-z.,\s+\-eE]+$")
COLOR_RE = re.compile(r"^(none|#[0-9a-fA-F]{3,8})$")
SVG_DATA_RE = re.compile(
    r"^data:image/svg\+xml;(?:charset=utf-8;)?base64,[A-Za-z0-9+/=]+$"
)

NUMERIC_RANGES = {
    "size": (5, 200),
    "x": (-200, 200),
    "y": (-200, 200),
    "rotation": (-360, 360),
    "opacity": (0, 100),
    "strokeWidth": (0, 20),
}


def default_bullet_config():
    return copy.deepcopy(DEFAULT_CONFIG)


def _validate_layer(layer, id_prefix, index, seen_ids):
    if not isinstance(layer, dict):
        return None, "图层必须是对象"

    layer_type = str(layer.get("type") or "preset").lower()
    if layer_type not in LAYER_TYPES:
        return None, "图层类型不合法"

    raw_id = str(layer.get("id") or f"{id_prefix}-{index + 1}")
    if not ID_RE.match(raw_id) or raw_id in seen_ids:
        raw_id = f"{id_prefix}-{index + 1}"
        suffix = 2
        while raw_id in seen_ids:
            raw_id = f"{id_prefix}-{index + 1}-{suffix}"
            suffix += 1
    seen_ids.add(raw_id)

    result = {"id": raw_id, "type": layer_type}

    if layer_type == "preset":
        shape = str(layer.get("shape") or "")
        if not SHAPE_RE.match(shape):
            return None, "预设形状名称不合法"
        result["shape"] = shape
    elif layer_type == "path":
        path = str(layer.get("path") or "").strip()
        if not path or len(path) > 2000 or not PATH_RE.match(path):
            return None, "SVG 路径格式不合法"
        result["path"] = path
    elif layer_type == "svg":
        data = str(layer.get("data") or "")
        if len(data) > 300000 or not SVG_DATA_RE.match(data):
            return None, "SVG 文件必须是 base64 编码的 SVG，且不能超过 300 KB"
        result["data"] = data

    for field, (minimum, maximum) in NUMERIC_RANGES.items():
        default_value = {"size": 100, "x": 0, "y": 0, "rotation": 0, "opacity": 100, "strokeWidth": 2}[field]
        value = layer.get(field, default_value)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None, f"{field} 必须是数字"
        if value < minimum or value > maximum:
            return None, f"{field} 超出范围"
        result[field] = round(float(value), 2)

    for field in ("fill", "stroke"):
        value = str(layer.get(field) or "none")
        if not COLOR_RE.match(value):
            return None, f"{field} 颜色格式不合法"
        result[field] = value

    return result, None


def _validate_variant(raw, label):
    if not isinstance(raw, dict):
        return None, f"{label}配置缺失"

    layers = raw.get("layers")
    if not isinstance(layers, list) or len(layers) < 1 or len(layers) > 24:
        return None, f"{label}至少需要 1 个图层，最多 24 个"

    validated_layers = []
    seen_ids = set()
    id_prefix = re.sub(r"[^a-z0-9_-]+", "-", label.lower()).strip("-") or "layer"
    for index, layer in enumerate(layers):
        validated, error = _validate_layer(layer, id_prefix, index, seen_ids)
        if error:
            return None, f"{label}第 {index + 1} 层：{error}"
        validated_layers.append(validated)

    return {"layers": validated_layers}, None


def normalize_bullet_config(config):
    default = default_bullet_config()
    if not isinstance(config, dict):
        return default

    normalized = {}
    for kind in KINDS:
        raw_kind = config.get(kind) if isinstance(config.get(kind), dict) else {}
        kind_config = (
            copy.deepcopy(raw_kind)
            if isinstance(raw_kind.get("layers"), list) and raw_kind.get("layers")
            else copy.deepcopy(default[kind])
        )

        raw_statuses = (
            raw_kind.get("statuses")
            if isinstance(raw_kind.get("statuses"), dict)
            else {}
        )
        statuses = {}
        for status, default_variant in default[kind].get("statuses", {}).items():
            raw_variant = raw_statuses.get(status)
            statuses[status] = (
                copy.deepcopy(raw_variant)
                if isinstance(raw_variant, dict)
                and isinstance(raw_variant.get("layers"), list)
                and raw_variant.get("layers")
                else copy.deepcopy(default_variant)
            )
        if statuses:
            kind_config["statuses"] = statuses

        normalized[kind] = kind_config

    return normalized


def validate_bullet_config(data):
    if not isinstance(data, dict):
        return None, "子弹配置必须是对象"

    config = {}
    for kind in KINDS:
        raw = data.get(kind)
        kind_config, error = _validate_variant(raw, kind)
        if error:
            return None, error

        raw_statuses = raw.get("statuses") if isinstance(raw, dict) else None
        statuses = {}
        if raw_statuses is not None:
            if not isinstance(raw_statuses, dict):
                return None, f"{kind} 状态配置必须是对象"
            for status in STATUSES:
                if status not in raw_statuses:
                    continue
                variant, status_error = _validate_variant(
                    raw_statuses[status],
                    f"{kind} {status} ",
                )
                if status_error:
                    return None, status_error
                statuses[status] = variant

        for status, default_variant in DEFAULT_CONFIG[kind].get("statuses", {}).items():
            statuses.setdefault(status, copy.deepcopy(default_variant))

        if statuses:
            kind_config["statuses"] = statuses
        config[kind] = kind_config

    return config, None


@bullet_style_bp.get("")
@login_required()
def get_bullet_style():
    style = BulletStyle.query.filter_by(user_id=g.current_user.id).first()
    return jsonify(
        {
            "config": normalize_bullet_config(style.config) if style else default_bullet_config(),
            "is_custom": bool(style),
        }
    )


@bullet_style_bp.put("")
@login_required()
def update_bullet_style():
    data = request.get_json(silent=True) or {}
    raw_config = data.get("config", data)
    config, error = validate_bullet_config(raw_config)
    if error:
        return jsonify({"message": error}), 400

    style = BulletStyle.query.filter_by(user_id=g.current_user.id).first()
    if style:
        style.config = config
    else:
        style = BulletStyle(user_id=g.current_user.id, config=config)
        db.session.add(style)
    db.session.commit()
    return jsonify({"message": "子弹样式已保存", "config": config, "is_custom": True})


@bullet_style_bp.delete("")
@login_required()
def reset_bullet_style():
    style = BulletStyle.query.filter_by(user_id=g.current_user.id).first()
    if style:
        db.session.delete(style)
        db.session.commit()
    return jsonify(
        {
            "message": "已恢复默认子弹样式",
            "config": default_bullet_config(),
            "is_custom": False,
        }
    )
