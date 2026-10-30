"""


Schema:
  TABLE scans (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp   TEXT,
      filename    TEXT,
      filepath    TEXT,
      media_type  TEXT,   -- 'image' | 'video'
      verdict     TEXT,   -- 'REAL' | 'AI GENERATED'
      probability REAL,
      confidence  REAL,
      face_detected INTEGER,  -- 0 | 1
      frames_analyzed INTEGER,
      file_size   INTEGER,
      width       INTEGER,
      height      INTEGER,
      duration    REAL
  )
"""

import os
import sqlite3
import logging
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'veridect.db')


#Connection helper

@contextmanager
def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error(f"DB error: {exc}")
        raise
    finally:
        conn.close()


#Initialisation

def init_db():
    """Create tables if they don't exist. Safe to call multiple times."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       TEXT    NOT NULL,
                filename        TEXT    NOT NULL,
                filepath        TEXT    NOT NULL,
                media_type      TEXT    NOT NULL,
                verdict         TEXT    NOT NULL,
                probability     REAL    NOT NULL DEFAULT 0,
                confidence      REAL    NOT NULL DEFAULT 0,
                face_detected   INTEGER NOT NULL DEFAULT 0,
                frames_analyzed INTEGER NOT NULL DEFAULT 1,
                file_size       INTEGER NOT NULL DEFAULT 0,
                width           INTEGER NOT NULL DEFAULT 0,
                height          INTEGER NOT NULL DEFAULT 0,
                duration        REAL    NOT NULL DEFAULT 0
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_ts ON scans(timestamp DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_verdict ON scans(verdict)")


#Write

def insert_scan(file_path: str, result: dict, media_type: str, meta: dict = None) -> int:
    """
    Insert a completed scan into the database.

    Args:
        file_path:  Full path to the analysed file.
        result:     Detection result dict from image/video detector.
        media_type: 'image' or 'video'.
        meta:       Optional file metadata dict from get_file_metadata().

    Returns:
        The row id of the inserted scan.
    """
    meta = meta or {}
    with _get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO scans
              (timestamp, filename, filepath, media_type, verdict,
               probability, confidence, face_detected, frames_analyzed,
               file_size, width, height, duration)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            datetime.now().isoformat(timespec='seconds'),
            os.path.basename(file_path),
            file_path,
            media_type,
            result.get('verdict', 'UNKNOWN'),
            round(result.get('probability', 0.0), 6),
            round(result.get('confidence', 0.0), 6),
            int(bool(result.get('face_detected', False))),
            result.get('frames_analyzed', 1),
            meta.get('size_bytes', 0),
            meta.get('width', 0),
            meta.get('height', 0),
            meta.get('duration', 0.0),
        ))
        return cur.lastrowid


#Read

def get_all_scans(limit: int = 500) -> list[dict]:
    """Return all scans ordered newest first."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM scans ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    """
    Return aggregated statistics across all scans.

    Returns dict with:
      total, real_count, fake_count, fake_pct,
      avg_confidence, image_count, video_count,
      last_scan_ts
    """
    with _get_conn() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*)                                     AS total,
                SUM(CASE WHEN verdict='REAL' THEN 1 ELSE 0 END)         AS real_count,
                SUM(CASE WHEN verdict='AI GENERATED' THEN 1 ELSE 0 END) AS fake_count,
                AVG(confidence)                              AS avg_confidence,
                SUM(CASE WHEN media_type='image' THEN 1 ELSE 0 END)     AS image_count,
                SUM(CASE WHEN media_type='video' THEN 1 ELSE 0 END)     AS video_count,
                MAX(timestamp)                               AS last_scan_ts
            FROM scans
        """).fetchone()

    total = row['total'] or 0
    fake  = row['fake_count'] or 0
    return {
        'total':          total,
        'real_count':     row['real_count'] or 0,
        'fake_count':     fake,
        'fake_pct':       round(fake / total * 100, 1) if total else 0.0,
        'avg_confidence': round((row['avg_confidence'] or 0) * 100, 1),
        'image_count':    row['image_count'] or 0,
        'video_count':    row['video_count'] or 0,
        'last_scan_ts':   row['last_scan_ts'] or '—',
    }


def search_scans(query: str = '', verdict_filter: str = '') -> list[dict]:
    """
    Search scans by filename and/or verdict.

    Args:
        query:          Partial filename match (case-insensitive).
        verdict_filter: 'REAL', 'AI GENERATED', or '' for all.
    """
    sql  = "SELECT * FROM scans WHERE 1=1"
    args = []

    if query:
        sql  += " AND filename LIKE ?"
        args.append(f"%{query}%")

    if verdict_filter:
        sql  += " AND verdict = ?"
        args.append(verdict_filter)

    sql += " ORDER BY id DESC LIMIT 300"

    with _get_conn() as conn:
        rows = conn.execute(sql, args).fetchall()
    return [dict(r) for r in rows]


#Delete

def delete_scan(scan_id: int) -> None:
    """Delete a single scan by id."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))


def clear_all_scans() -> None:
    """Delete every scan record."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM scans")
