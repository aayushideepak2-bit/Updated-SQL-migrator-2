from typing import Any, Dict, List
from sqlalchemy import MetaData, Table, Column, inspect
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

from backend.database.connection_manager import create_engine_for_config
from backend.validators.migration_validator import validate_table_counts
from backend.converters.datatype_mapper import map_datatype
from backend.converters.migration_tracker import migrate_with_tracking, persist_migration_issues


def build_table_schema(source_engine, table_name: str, target_db_type: str) -> Table:
    """Build a target SQLAlchemy Table object from a source table schema."""
    source_meta = MetaData()
    target_meta = MetaData()
    source_table = Table(table_name, source_meta, autoload_with=source_engine)

    columns = []
    for column in source_table.columns:
        mapped_type = map_datatype(str(column.type), target_db_type)
        column_args = {
            "primary_key": column.primary_key,
            "nullable": column.nullable,
        }
        columns.append(Column(column.name, mapped_type, **column_args))

    return Table(table_name, target_meta, *columns)


def migrate_sql_to_sql(payload: Dict[str, Any], migration_id: int = None) -> Dict[str, Any]:
    """Perform a SQL-to-SQL migration workflow between two databases.

    ``migration_id`` is optional — when provided (i.e. the caller already
    created a Migration record), any failed/cancelled rows are persisted to
    the migration_row_issues table so they're visible via
    /api/migrations/<id>/issues. Without it, tracking still happens but stays
    in-memory only (returned in the response, not queryable later).
    """
    source_config = {
        "db_type": payload.get("source_db_type"),
        "username": payload.get("source_username"),
        "password": payload.get("source_password"),
        "host": payload.get("source_host"),
        "port": payload.get("source_port"),
        "database": payload.get("source_database"),
    }
    target_config = {
        "db_type": payload.get("target_db_type"),
        "username": payload.get("target_username"),
        "password": payload.get("target_password"),
        "host": payload.get("target_host"),
        "port": payload.get("target_port"),
        "database": payload.get("target_database"),
    }
    selected_tables = payload.get("tables") or []

    source_engine = create_engine_for_config(source_config)
    target_engine = create_engine_for_config(target_config)
    inspector = inspect(source_engine)
    source_tables = inspector.get_table_names()
    tables = selected_tables if selected_tables else source_tables

    if not tables:
        raise ValueError("No tables were selected for migration.")

    summary: List[Dict[str, Any]] = []
    for table_name in tables:
        if table_name not in source_tables:
            summary.append({"table": table_name, "status": "skipped", "reason": "Table not found on source."})
            continue

        try:
            target_table = build_table_schema(source_engine, table_name, target_config["db_type"])
            target_table.metadata.create_all(target_engine)

            data_frame = pd.read_sql_table(table_name, source_engine)
            if not data_frame.empty:
                # Use tracking migration for row-level error handling
                migration_report = migrate_with_tracking(data_frame, target_engine, table_name)
                if migration_id:
                    persist_migration_issues(migration_report, migration_id)
                validation = validate_table_counts(source_engine, target_engine, table_name)
                summary.append({
                    "table": table_name,
                    "rows_transferred": migration_report["successful_count"],
                    "rows_failed": migration_report["summary"]["failed"],
                    "rows_cancelled": migration_report["summary"]["cancelled"],
                    "validation": validation,
                    "migration_report": migration_report,
                    "status": "completed",
                })
            else:
                summary.append({
                    "table": table_name,
                    "rows_transferred": 0,
                    "validation": {"source_row_count": 0, "target_row_count": 0, "match": True},
                    "status": "completed",
                })
        except SQLAlchemyError as error:
            summary.append({"table": table_name, "status": "failed", "error": str(error)})

    return {
        "summary": summary,
        "tables": tables,
        "source_db": source_config,
        "target_db": target_config,
    }