"""Application settings loaded from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    alert_threshold: int
    database_path: Path

    @classmethod
    def from_environment(cls) -> "Settings":
        raw_threshold = os.getenv("IPO_ALERT_THRESHOLD", "3")
        try:
            threshold = int(raw_threshold)
        except ValueError as exc:
            raise ValueError("IPO_ALERT_THRESHOLD must be a non-negative integer.") from exc
        if threshold < 0:
            raise ValueError("IPO_ALERT_THRESHOLD must be a non-negative integer.")

        database_path = Path(os.getenv("IPO_DATABASE_PATH", "data/ipos.sqlite3"))
        return cls(alert_threshold=threshold, database_path=database_path)
