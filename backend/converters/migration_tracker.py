"""Migration tracking for row-level error handling during SQL-to-SQL migrations."""

from typing import Any, Dict, List
import pandas as pd
from sqlalchemy.engine import Engine


def migrate_with_tracking(
    data_frame: pd.DataFrame,
    target_engine: Engine,
    table_name: str,
) -> Dict[str, Any]:
    """
    Insert DataFrame rows into target table, tracking successes and failures.
    
    Returns a dict with successful_count, and a summary dict tracking
    failed and cancelled rows.
    """
    successful_count = 0
    failed_rows = []
    
    try:
        data_frame.to_sql(table_name, target_engine, if_exists="append", index=False)
        successful_count = len(data_frame)
    except Exception as exc:
        # Fall back to row-by-row insertion to track failures per row
        for idx, row in data_frame.iterrows():
            try:
                row_df = pd.DataFrame([row])
                row_df.to_sql(table_name, target_engine, if_exists="append", index=False)
                successful_count += 1
            except Exception:
                failed_rows.append(idx)
    
    return {
        "successful_count": successful_count,
        "summary": {
            "failed": len(failed_rows),
            "cancelled": 0,
        },
        "failed_row_indices": failed_rows,
    }


def persist_migration_issues(
    migration_report: Dict[str, Any],
    migration_id: int,
) -> None:
    """
    Persist row-level migration failures to the database.
    
    This would normally insert records into a migration_row_issues table,
    but for now this is a no-op stub since the table may not be fully
    set up in all deployments.
    """
    pass
