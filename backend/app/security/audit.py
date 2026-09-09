import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from backend.app.config import settings

logger = logging.getLogger("agni.security.audit")


class AuditLedger:
    """Local SQLite audit ledger recording all agent runs and deliverables."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.AUDIT_DB_PATH
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        task_prompt TEXT,
                        selected_model TEXT,
                        tools_called TEXT,
                        citations_count INTEGER DEFAULT 0,
                        deliverable_paths TEXT,
                        verification_status TEXT,
                        air_gap_compliant INTEGER DEFAULT 1
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize SQLite audit database: {e}")

    def log_task_execution(
        self,
        task_id: str,
        task_prompt: str,
        selected_model: Optional[str],
        tools_called: List[str],
        citations_count: int,
        deliverable_paths: List[str],
        verification_status: str,
    ):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO audit_records (
                        task_id, timestamp, task_prompt, selected_model,
                        tools_called, citations_count, deliverable_paths,
                        verification_status, air_gap_compliant
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    task_id,
                    datetime.utcnow().isoformat(),
                    task_prompt,
                    selected_model or "unknown",
                    json.dumps(tools_called),
                    citations_count,
                    json.dumps(deliverable_paths),
                    verification_status,
                ))
                conn.commit()
                logger.info(f"Recorded audit log for task '{task_id}' into {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to write audit entry: {e}")

    def get_recent_records(self, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM audit_records ORDER BY id DESC LIMIT ?", (limit,))
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Failed to query audit entries: {e}")
            return []


# Global audit ledger instance
audit_ledger = AuditLedger()
