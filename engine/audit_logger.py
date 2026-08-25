import sqlite3
import json
import os
from datetime import datetime, timezone
from utils.logger import get_logger

log = get_logger("audit_logger")
DB_PATH = "telemetry.db"

def init_telemetry_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS telemetry_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT,
                    timestamp TEXT,
                    target_document TEXT,
                    chunk_index INTEGER,
                    tokens_used INTEGER,
                    latency_ms REAL,
                    status TEXT,
                    error_message TEXT,
                    raw_llm_response TEXT
                )
            ''')
            conn.commit()
    except Exception as e:
        log.error("failed to initialize telemetry db", error=str(e))

def log_telemetry(
    trace_id: str,
    target_document: str,
    chunk_index: int,
    tokens_used: int,
    latency_ms: float,
    status: str,
    error_message: str = "",
    raw_llm_response: str = ""
):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO telemetry_logs (
                    trace_id, timestamp, target_document, chunk_index,
                    tokens_used, latency_ms, status, error_message, raw_llm_response
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trace_id,
                datetime.now(timezone.utc).isoformat(),
                target_document,
                chunk_index,
                tokens_used,
                latency_ms,
                status,
                error_message,
                raw_llm_response
            ))
            conn.commit()
    except Exception as e:
        log.error("failed to log telemetry", error=str(e))

def get_recent_failures(limit: int = 50):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM telemetry_logs 
                WHERE status != 'success' 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        log.error("failed to fetch recent failures", error=str(e))
        return []
