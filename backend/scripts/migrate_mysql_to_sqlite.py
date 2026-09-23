import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import MetaData, Table, func, select
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy import create_engine


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_TARGET_URL = f"sqlite:///{(BASE_DIR / 'data' / 'bullet_journal.db').as_posix()}"
TABLE_ORDER = ["users", "collections", "journal_entries", "bullet_styles"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="把旧 MySQL 数据迁移到 SQLite。",
    )
    parser.add_argument(
        "--source",
        default=os.getenv("SOURCE_DATABASE_URL"),
        help="旧 MySQL 连接串，例如 mysql+pymysql://root:password@127.0.0.1:3306/bullet_journal?charset=utf8mb4",
    )
    parser.add_argument(
        "--target",
        default=os.getenv("TARGET_DATABASE_URL") or os.getenv("DATABASE_URL") or DEFAULT_TARGET_URL,
        help="目标 SQLite 连接串，默认使用 backend/data/bullet_journal.db",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="目标库已有数据时先清空再导入。",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.source:
        raise SystemExit("请通过 --source 或 SOURCE_DATABASE_URL 提供旧 MySQL 连接串。")

    os.environ["DATABASE_URL"] = args.target
    os.environ["AUTO_CREATE_TABLES"] = "false"
    sys.path.insert(0, str(BASE_DIR))

    from app import create_app
    from app.extensions import db

    app = create_app()
    source_engine = create_engine(args.source, pool_pre_ping=True)
    source_metadata = MetaData()
    source_tables = {}

    for table_name in TABLE_ORDER:
        try:
            source_tables[table_name] = Table(
                table_name,
                source_metadata,
                autoload_with=source_engine,
            )
        except NoSuchTableError:
            source_tables[table_name] = None

    with app.app_context():
        db.create_all()
        target_tables = db.metadata.tables

        with source_engine.connect() as source_connection, db.engine.begin() as target_connection:
            if not args.force:
                for table_name in TABLE_ORDER:
                    target_table = target_tables.get(table_name)
                    if target_table is None:
                        continue
                    existing = target_connection.execute(
                        select(func.count()).select_from(target_table)
                    ).scalar()
                    if existing:
                        raise SystemExit(
                            f"目标库表 {table_name} 已有 {existing} 条数据；"
                            "如需覆盖请加 --force。"
                        )

            if args.force:
                for table_name in reversed(TABLE_ORDER):
                    target_table = target_tables.get(table_name)
                    if target_table is not None:
                        target_connection.execute(target_table.delete())

            copied = {}
            for table_name in TABLE_ORDER:
                source_table = source_tables.get(table_name)
                target_table = target_tables.get(table_name)
                if source_table is None or target_table is None:
                    copied[table_name] = 0
                    continue

                rows = source_connection.execute(select(source_table)).mappings().all()
                if rows:
                    target_connection.execute(
                        target_table.insert(),
                        [dict(row) for row in rows],
                    )
                copied[table_name] = len(rows)

    print("MySQL -> SQLite migration completed.")
    for table_name, count in copied.items():
        print(f"{table_name}: {count}")


if __name__ == "__main__":
    main()
