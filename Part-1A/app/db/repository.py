"""Parameterized SQLite repository for IPO records."""

import sqlite3
from datetime import UTC, datetime
from typing import Any

from app.core.config import Settings
from app.core.errors import DuplicateIPOError, IPOStorageError
from app.db.connection import connect_database
from app.db.models import IPORecord
from app.utils.normalization import matches_duplicate_identity

IPO_COLUMNS = (
    "id",
    "company_name",
    "opening_date",
    "closing_date",
    "allotment_date",
    "refund_date",
    "listing_date",
    "created_at",
    "updated_at",
)


class IPORepository:
    def __init__(self, settings: Settings):
        self.settings = settings

    @staticmethod
    def _record(row: sqlite3.Row | None) -> IPORecord | None:
        return IPORecord.from_row(dict(row)) if row is not None else None

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")

    def create(self, values: dict[str, Any]) -> IPORecord:
        now = self._now()
        try:
            with connect_database(self.settings) as connection:
                connection.execute("BEGIN IMMEDIATE")
                if self._is_duplicate(connection, values, exclude_id=None):
                    raise DuplicateIPOError(
                        "Duplicate IPO record: the same normalized company name, opening date, "
                        "and closing date already exists."
                    )
                cursor = connection.execute(
                    """
                    INSERT INTO ipos (
                        company_name, opening_date, closing_date, allotment_date,
                        refund_date, listing_date, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        values["company_name"],
                        values["opening_date"].isoformat(),
                        values["closing_date"].isoformat(),
                        _date_text(values["allotment_date"]),
                        _date_text(values["refund_date"]),
                        _date_text(values["listing_date"]),
                        now,
                        now,
                    ),
                )
                row = connection.execute(
                    "SELECT * FROM ipos WHERE id = ?", (cursor.lastrowid,)
                ).fetchone()
                record = self._record(row)
            if record is None:
                raise IPOStorageError("The saved IPO record could not be retrieved.")
            return record
        except DuplicateIPOError:
            raise
        except sqlite3.DatabaseError as exc:
            raise IPOStorageError(
                "The IPO record could not be saved due to a database error."
            ) from exc

    def get(self, ipo_id: int) -> IPORecord | None:
        try:
            with connect_database(self.settings) as connection:
                row = connection.execute("SELECT * FROM ipos WHERE id = ?", (ipo_id,)).fetchone()
            return self._record(row)
        except sqlite3.DatabaseError as exc:
            raise IPOStorageError("IPO records could not be read due to a database error.") from exc

    def list_all(self) -> list[IPORecord]:
        try:
            with connect_database(self.settings) as connection:
                rows = connection.execute("SELECT * FROM ipos ORDER BY id ASC").fetchall()
            return [IPORecord.from_row(dict(row)) for row in rows]
        except sqlite3.DatabaseError as exc:
            raise IPOStorageError("IPO records could not be read due to a database error.") from exc

    def update(self, ipo_id: int, values: dict[str, Any]) -> IPORecord | None:
        now = self._now()
        try:
            with connect_database(self.settings) as connection:
                connection.execute("BEGIN IMMEDIATE")
                existing_row = connection.execute(
                    "SELECT * FROM ipos WHERE id = ?", (ipo_id,)
                ).fetchone()
                if existing_row is None:
                    return None
                if self._is_duplicate(connection, values, exclude_id=ipo_id):
                    raise DuplicateIPOError(
                        "Duplicate IPO record: the update matches another record's normalized "
                        "company name, opening date, and closing date."
                    )
                connection.execute(
                    """
                    UPDATE ipos
                    SET company_name = ?, opening_date = ?, closing_date = ?,
                        allotment_date = ?, refund_date = ?, listing_date = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        values["company_name"],
                        values["opening_date"].isoformat(),
                        values["closing_date"].isoformat(),
                        _date_text(values["allotment_date"]),
                        _date_text(values["refund_date"]),
                        _date_text(values["listing_date"]),
                        now,
                        ipo_id,
                    ),
                )
                row = connection.execute("SELECT * FROM ipos WHERE id = ?", (ipo_id,)).fetchone()
                record = self._record(row)
            return record
        except DuplicateIPOError:
            raise
        except sqlite3.DatabaseError as exc:
            raise IPOStorageError(
                "The IPO record could not be updated due to a database error."
            ) from exc

    def delete(self, ipo_id: int) -> bool:
        try:
            with connect_database(self.settings) as connection:
                cursor = connection.execute("DELETE FROM ipos WHERE id = ?", (ipo_id,))
            return cursor.rowcount > 0
        except sqlite3.DatabaseError as exc:
            raise IPOStorageError(
                "The IPO record could not be deleted due to a database error."
            ) from exc

    @staticmethod
    def _is_duplicate(
        connection: sqlite3.Connection,
        values: dict[str, Any],
        exclude_id: int | None,
    ) -> bool:
        rows = connection.execute(
            "SELECT id, company_name, opening_date, closing_date FROM ipos"
        ).fetchall()
        return any(
            row["id"] != exclude_id
            and matches_duplicate_identity(
                row["company_name"],
                row["opening_date"],
                row["closing_date"],
                values["company_name"],
                values["opening_date"],
                values["closing_date"],
            )
            for row in rows
        )


def _date_text(value: Any) -> str | None:
    return value.isoformat() if value is not None else None
