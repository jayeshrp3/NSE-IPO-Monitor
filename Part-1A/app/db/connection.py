"""SQLite connection lifecycle and schema initialization."""

import sqlite3

from app.core.config import Settings


def connect_database(settings: Settings) -> sqlite3.Connection:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(settings: Settings) -> None:
    with connect_database(settings) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ipos (
                id INTEGER PRIMARY KEY,
                company_name TEXT NOT NULL CHECK (length(trim(company_name)) > 0),
                opening_date TEXT NOT NULL
                    CHECK (date(opening_date) IS NOT NULL AND date(opening_date) = opening_date),
                closing_date TEXT NOT NULL
                    CHECK (date(closing_date) IS NOT NULL AND date(closing_date) = closing_date),
                allotment_date TEXT
                    CHECK (allotment_date IS NULL OR
                           (date(allotment_date) IS NOT NULL
                            AND date(allotment_date) = allotment_date)),
                refund_date TEXT
                    CHECK (refund_date IS NULL OR
                           (date(refund_date) IS NOT NULL AND date(refund_date) = refund_date)),
                listing_date TEXT
                    CHECK (listing_date IS NULL OR
                           (date(listing_date) IS NOT NULL AND date(listing_date) = listing_date)),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                CHECK (closing_date >= opening_date)
            )
            """
        )
