import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import settings

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_runs():
    return {
        "runs": [],
        "count": 0,
    }
def _db_path() -> str:
    if settings.database_url.startswith("sqlite:///"):
        return settings.database_url.replace("sqlite:///", "", 1)
    return "./data/blog_engine.db"


class BlogRepository:
    def __init__(self):
        path = Path(_db_path())
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init()

    def _init(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT,
                primary_keyword TEXT,
                content_hash TEXT NOT NULL UNIQUE,
                trend_key TEXT,
                country TEXT,
                category TEXT,
                status TEXT NOT NULL,
                published_at TEXT,
                created_at TEXT NOT NULL,
                research_json TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug);
            CREATE INDEX IF NOT EXISTS idx_articles_trend ON articles(trend_key);
            CREATE INDEX IF NOT EXISTS idx_articles_created ON articles(created_at);

            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT UNIQUE NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                status TEXT NOT NULL,
                message TEXT,
                topic TEXT,
                article_title TEXT
            );

            CREATE TABLE IF NOT EXISTS trend_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trend_key TEXT NOT NULL,
                query TEXT NOT NULL,
                country_code TEXT NOT NULL,
                category TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                score REAL,
                raw_json TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_trend_history_key
            ON trend_history(trend_key, observed_at);
            """
        )
        self.conn.commit()

    @staticmethod
    def normalize(text: str) -> str:
        import re
        return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

    @classmethod
    def trend_key(cls, query: str) -> str:
        return cls.normalize(query)

    @classmethod
    def content_hash(cls, title: str, content: str) -> str:
        value = f"{cls.normalize(title)}\n{cls.normalize(content)}".encode("utf-8")
        return hashlib.sha256(value).hexdigest()

    def recent_titles(self, limit: int = 250) -> list[str]:
        rows = self.conn.execute(
            "SELECT title FROM articles ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [row["title"] for row in rows]

    def all_title_slug_keyword_rows(self, limit: int = 500) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT title, slug, primary_keyword FROM articles ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def article_exists(self, title: str, slug: str, content: str) -> bool:
        norm_title = self.normalize(title)
        norm_slug = self.normalize(slug)
        digest = self.content_hash(title, content)
        rows = self.conn.execute(
            "SELECT title, slug, content_hash FROM articles"
        ).fetchall()
        for row in rows:
            if self.normalize(row["title"]) == norm_title:
                return True
            if norm_slug and self.normalize(row["slug"] or "") == norm_slug:
                return True
            if row["content_hash"] == digest:
                return True
        return False

    def similar_topic_recently_used(self, trend_key: str, days: int = 30) -> bool:
        cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
        row = self.conn.execute(
            """
            SELECT 1 FROM articles
            WHERE trend_key = ?
            AND (julianday('now') - julianday(created_at)) * 24 < ?
            LIMIT 1
            """,
            (trend_key, days * 24),
        ).fetchone()
        return row is not None

    def record_article(
        self,
        *,
        title: str,
        slug: str,
        primary_keyword: str,
        content: str,
        trend_key: str,
        country: str,
        category: str,
        status: str,
        research: dict[str, Any],
    ) -> None:
        digest = self.content_hash(title, content)
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            """
            INSERT OR IGNORE INTO articles
            (title, slug, primary_keyword, content_hash, trend_key, country,
             category, status, published_at, created_at, research_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                slug,
                primary_keyword,
                digest,
                trend_key,
                country,
                category,
                status,
                now if status == "published" else None,
                now,
                json.dumps(research, ensure_ascii=False),
            ),
        )
        self.conn.commit()

    def add_trend(self, topic: dict[str, Any], score: float) -> None:
        self.conn.execute(
            """
            INSERT INTO trend_history
            (trend_key, query, country_code, category, observed_at, score, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.trend_key(topic.get("query", "")),
                topic.get("query", ""),
                topic.get("country_code", ""),
                topic.get("category", ""),
                datetime.now(timezone.utc).isoformat(),
                score,
                json.dumps(topic, ensure_ascii=False),
            ),
        )
        self.conn.commit()

    def create_run(self, run_id: str, status: str, message: str = ""):
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            """
            INSERT INTO runs(run_id, started_at, status, message)
            VALUES (?, ?, ?, ?)
            """,
            (run_id, now, status, message),
        )
        self.conn.commit()

    def finish_run(
        self,
        run_id: str,
        status: str,
        message: str,
        topic: str | None = None,
        article_title: str | None = None,
    ):
        self.conn.execute(
            """
            UPDATE runs
            SET finished_at = ?, status = ?, message = ?, topic = ?, article_title = ?
            WHERE run_id = ?
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                status,
                message,
                topic,
                article_title,
                run_id,
            ),
        )
        self.conn.commit()


    def published_today_count(self) -> int:
        row = self.conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM articles
            WHERE status = 'published'
              AND date(published_at) = date('now')
            """
        ).fetchone()
        return int(row["count"] if row else 0)

    def recent_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM runs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def published_articles(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT title, slug, primary_keyword, country, category, published_at
            FROM articles
            WHERE status = 'published'
            ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
