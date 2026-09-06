from dataclasses import dataclass
from datetime import datetime


@dataclass
class RunRecord:
    run_id: str
    started_at: str
    finished_at: str | None
    status: str
    message: str
    topic: str | None = None
    article_title: str | None = None
