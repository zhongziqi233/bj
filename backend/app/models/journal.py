from datetime import datetime, timezone

from ..extensions import db


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Collection(db.Model):
    __tablename__ = "collections"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )

    user = db.relationship("User", back_populates="collections")
    entries = db.relationship(
        "Entry",
        back_populates="collection",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="Entry.created_at",
    )

    def to_dict(self, include_entries=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "entry_count": len(self.entries),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_entries:
            data["entries"] = [entry.to_dict() for entry in self.entries]
        return data


class Entry(db.Model):
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    collection_id = db.Column(
        db.Integer,
        db.ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    kind = db.Column(db.String(20), nullable=False, default="task")
    content = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open")
    important = db.Column(db.Boolean, nullable=False, default=False)
    log_type = db.Column(db.String(20), nullable=False, default="daily", index=True)
    entry_date = db.Column(db.Date, nullable=True, index=True)
    period_date = db.Column(db.Date, nullable=True, index=True)
    migrated_to_date = db.Column(db.Date, nullable=True)
    scheduled_date = db.Column(db.Date, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )

    user = db.relationship("User", back_populates="entries")
    collection = db.relationship("Collection", back_populates="entries")

    def to_dict(self):
        return {
            "id": self.id,
            "kind": self.kind,
            "content": self.content,
            "status": self.status,
            "important": self.important,
            "log_type": self.log_type,
            "entry_date": self.entry_date.isoformat() if self.entry_date else None,
            "period_date": self.period_date.isoformat() if self.period_date else None,
            "migrated_to_date": (
                self.migrated_to_date.isoformat() if self.migrated_to_date else None
            ),
            "scheduled_date": (
                self.scheduled_date.isoformat() if self.scheduled_date else None
            ),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "collection_id": self.collection_id,
            "collection": (
                {"id": self.collection.id, "name": self.collection.name}
                if self.collection
                else None
            ),
        }


class BulletStyle(db.Model):
    __tablename__ = "bullet_styles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    config = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )

    user = db.relationship("User", back_populates="bullet_style")

    def to_dict(self):
        return {
            "id": self.id,
            "config": self.config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
