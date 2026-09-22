from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, g, jsonify, request
from sqlalchemy import and_, or_

from ..extensions import db
from ..models import Collection, Entry
from ..utils import (
    login_required,
    parse_bool,
    parse_date,
    parse_month,
    parse_optional_date,
)
from ..utils.dates import add_months

entries_bp = Blueprint("entries", __name__)

KINDS = {"task", "event", "note"}
LOG_TYPES = {"daily", "monthly", "future", "collection"}
STATUSES = {"open", "completed", "postponed", "migrated", "scheduled", "cancelled"}


def _owned_entry(entry_id):
    return Entry.query.filter_by(id=entry_id, user_id=g.current_user.id).first()


def _owned_collection(collection_id):
    if not collection_id:
        return None
    return Collection.query.filter_by(
        id=collection_id,
        user_id=g.current_user.id,
    ).first()


def _validate_payload(data, entry=None):
    kind = (data.get("kind") or (entry.kind if entry else "task")).lower()
    log_type = (data.get("log_type") or (entry.log_type if entry else "daily")).lower()
    status = (data.get("status") or (entry.status if entry else "open")).lower()
    content = data.get("content", entry.content if entry else "")
    content = (content or "").strip()

    if kind not in KINDS:
        return None, "记录类型必须是 task、event 或 note"
    if log_type not in LOG_TYPES:
        return None, "日志类型必须是 daily、monthly、future 或 collection"
    if status not in STATUSES:
        return None, "记录状态不合法"
    if not content:
        return None, "记录内容不能为空"
    if len(content) > 500:
        return None, "记录内容不能超过 500 个字符"

    payload = {"kind": kind, "log_type": log_type, "status": status, "content": content}

    try:
        entry_date = data.get("entry_date") if "entry_date" in data else (
            entry.entry_date if entry else None
        )
        period_date = data.get("period_date") if "period_date" in data else (
            entry.period_date if entry else None
        )
        payload["entry_date"] = parse_optional_date(entry_date)
        payload["period_date"] = parse_optional_date(period_date)
        if "migrated_to_date" in data:
            payload["migrated_to_date"] = parse_optional_date(data.get("migrated_to_date"))
        if "scheduled_date" in data:
            payload["scheduled_date"] = parse_optional_date(data.get("scheduled_date"))
    except ValueError as exc:
        return None, str(exc)

    if "important" in data:
        payload["important"] = parse_bool(data.get("important"), entry.important if entry else False)

    if "collection_id" in data:
        payload["collection_id"] = data.get("collection_id")
    elif entry is not None:
        payload["collection_id"] = entry.collection_id
    else:
        payload["collection_id"] = None

    if log_type == "daily" and not payload.get("entry_date"):
        payload["entry_date"] = date.today()

    if log_type == "monthly":
        if payload.get("entry_date") and not payload.get("period_date"):
            payload["period_date"] = payload["entry_date"].replace(day=1)
        if not payload.get("entry_date") and not payload.get("period_date"):
            return None, "月度记录需要日期或所属月份"

    if log_type == "future":
        if not payload.get("period_date") and payload.get("entry_date"):
            payload["period_date"] = payload["entry_date"].replace(day=1)
        if not payload.get("period_date"):
            return None, "未来记录需要目标月份"

    if log_type == "collection":
        collection = _owned_collection(payload.get("collection_id"))
        if not collection:
            return None, "请选择属于自己的集合"

    if log_type != "collection" and payload.get("collection_id"):
        payload["collection_id"] = None

    return payload, None


@entries_bp.get("")
@login_required()
def list_entries():
    log_type = (request.args.get("log_type") or "daily").lower()
    if log_type not in LOG_TYPES:
        return jsonify({"message": "日志类型不合法"}), 400

    query = Entry.query.filter_by(user_id=g.current_user.id, log_type=log_type)

    if log_type == "daily":
        try:
            day = parse_date(request.args.get("date")) or date.today()
        except ValueError as exc:
            return jsonify({"message": str(exc)}), 400
        query = query.filter(Entry.entry_date == day)
        query = query.order_by(Entry.created_at.asc())

    elif log_type == "monthly":
        try:
            month_start = parse_month(request.args.get("month"))
        except ValueError as exc:
            return jsonify({"message": str(exc)}), 400
        if not month_start:
            today = date.today()
            month_start = today.replace(day=1)
        next_month = add_months(month_start, 1)
        query = query.filter(
            or_(
                Entry.period_date == month_start,
                and_(Entry.entry_date >= month_start, Entry.entry_date < next_month),
            )
        ).order_by(Entry.entry_date.asc(), Entry.created_at.asc())

    elif log_type == "future":
        try:
            year = int(request.args.get("year") or date.today().year)
        except ValueError:
            return jsonify({"message": "年份格式不正确"}), 400
        year_start = date(year, 1, 1)
        year_end = date(year + 1, 1, 1)
        query = query.filter(
            or_(
                and_(Entry.period_date >= year_start, Entry.period_date < year_end),
                and_(Entry.entry_date >= year_start, Entry.entry_date < year_end),
            )
        ).order_by(Entry.period_date.asc(), Entry.created_at.asc())

    elif log_type == "collection":
        collection_id = request.args.get("collection_id", type=int)
        collection = _owned_collection(collection_id)
        if not collection:
            return jsonify({"message": "集合不存在"}), 404
        query = query.filter(Entry.collection_id == collection.id).order_by(
            Entry.created_at.asc()
        )

    items = query.limit(1000).all()
    return jsonify({"items": [entry.to_dict() for entry in items]})


@entries_bp.post("")
@login_required()
def create_entry():
    data = request.get_json(silent=True) or {}
    payload, error = _validate_payload(data)
    if error:
        return jsonify({"message": error}), 400

    entry = Entry(user_id=g.current_user.id, **payload)
    if entry.status == "completed":
        entry.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.session.add(entry)
    db.session.commit()
    return jsonify({"message": "记录已创建", "entry": entry.to_dict()}), 201


@entries_bp.patch("/<int:entry_id>")
@login_required()
def update_entry(entry_id):
    entry = _owned_entry(entry_id)
    if not entry:
        return jsonify({"message": "记录不存在"}), 404

    data = request.get_json(silent=True) or {}
    payload, error = _validate_payload(data, entry=entry)
    if error:
        return jsonify({"message": error}), 400

    previous_status = entry.status
    for key, value in payload.items():
        setattr(entry, key, value)

    if entry.status == "completed" and previous_status != "completed":
        entry.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    elif entry.status != "completed":
        entry.completed_at = None

    db.session.commit()
    return jsonify({"message": "记录已更新", "entry": entry.to_dict()})


@entries_bp.delete("/<int:entry_id>")
@login_required()
def delete_entry(entry_id):
    entry = _owned_entry(entry_id)
    if not entry:
        return jsonify({"message": "记录不存在"}), 404
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "记录已删除"})


@entries_bp.post("/<int:entry_id>/migrate")
@login_required()
def migrate_entry(entry_id):
    entry = _owned_entry(entry_id)
    if not entry:
        return jsonify({"message": "记录不存在"}), 404
    if entry.kind != "task":
        return jsonify({"message": "只有任务可以迁移"}), 400
    if entry.status != "open":
        return jsonify({"message": "只有待办任务可以迁移"}), 400

    data = request.get_json(silent=True) or {}
    try:
        target_date = parse_date(data.get("target_date"))
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400
    if not target_date:
        return jsonify({"message": "请选择迁移日期"}), 400

    new_entry = Entry(
        user_id=g.current_user.id,
        kind="task",
        content=entry.content,
        status="open",
        important=entry.important,
        log_type="daily",
        entry_date=target_date,
    )
    entry.status = "migrated"
    entry.migrated_to_date = target_date
    db.session.add(new_entry)
    db.session.commit()
    return jsonify(
        {
            "message": f"任务已迁移到 {target_date.isoformat()}",
            "entry": entry.to_dict(),
            "new_entry": new_entry.to_dict(),
        }
    )


@entries_bp.post("/<int:entry_id>/postpone")
@login_required()
def postpone_entry(entry_id):
    entry = _owned_entry(entry_id)
    if not entry:
        return jsonify({"message": "记录不存在"}), 404
    if entry.kind != "task":
        return jsonify({"message": "只有任务可以推迟"}), 400
    if entry.status != "open":
        return jsonify({"message": "只有待办任务可以推迟"}), 400

    source_date = entry.entry_date or date.today()
    target_date = source_date + timedelta(days=1)
    new_entry = Entry(
        user_id=g.current_user.id,
        kind="task",
        content=entry.content,
        status="open",
        important=entry.important,
        log_type="daily",
        entry_date=target_date,
    )
    entry.status = "postponed"
    entry.migrated_to_date = target_date
    db.session.add(new_entry)
    db.session.commit()
    return jsonify(
        {
            "message": f"任务已推迟到 {target_date.isoformat()}",
            "entry": entry.to_dict(),
            "new_entry": new_entry.to_dict(),
        }
    )


@entries_bp.post("/<int:entry_id>/schedule")
@login_required()
def schedule_entry(entry_id):
    entry = _owned_entry(entry_id)
    if not entry:
        return jsonify({"message": "记录不存在"}), 404
    if entry.status != "open":
        return jsonify({"message": "只有待办记录可以安排"}), 400

    data = request.get_json(silent=True) or {}
    try:
        target_date = parse_date(data.get("target_date"))
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400
    if not target_date:
        return jsonify({"message": "请选择目标月份"}), 400

    month_date = target_date.replace(day=1)
    new_entry = Entry(
        user_id=g.current_user.id,
        kind=entry.kind,
        content=entry.content,
        status="open",
        important=entry.important,
        log_type="future",
        period_date=month_date,
    )
    entry.status = "scheduled"
    entry.scheduled_date = target_date
    db.session.add(new_entry)
    db.session.commit()
    return jsonify(
        {
            "message": f"已安排到 {month_date.strftime('%Y-%m')} 的未来日志",
            "entry": entry.to_dict(),
            "new_entry": new_entry.to_dict(),
        }
    )
