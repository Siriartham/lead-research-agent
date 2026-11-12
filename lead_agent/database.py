"""SQLite persistence helpers for lead records."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "leads.db"

LEAD_FIELDS = (
    "company_name",
    "website",
    "contact_name",
    "job_title",
    "email",
    "industry",
    "location",
    "research_notes",
    "source_urls",
    "ai_summary",
    "fit_score",
)


@contextmanager
def _connect(db_path: str | Path = DEFAULT_DB_PATH) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    """Create the leads table if it does not already exist."""
    with _connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                website TEXT NOT NULL DEFAULT '',
                contact_name TEXT NOT NULL DEFAULT '',
                job_title TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL DEFAULT '',
                industry TEXT NOT NULL DEFAULT '',
                location TEXT NOT NULL DEFAULT '',
                research_notes TEXT NOT NULL DEFAULT '',
                source_urls TEXT NOT NULL DEFAULT '',
                ai_summary TEXT NOT NULL DEFAULT '',
                fit_score INTEGER CHECK (fit_score IS NULL OR fit_score BETWEEN 1 AND 5),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def list_leads(
    search_term: str = "", db_path: str | Path = DEFAULT_DB_PATH
) -> list[dict[str, Any]]:
    """Return all leads, or those matching a company/contact/email search."""
    pattern = f"%{search_term.strip()}%"
    with _connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM leads
            WHERE ? = '%%'
               OR company_name LIKE ?
               OR contact_name LIKE ?
               OR email LIKE ?
            ORDER BY updated_at DESC, id DESC
            """,
            (pattern, pattern, pattern, pattern),
        ).fetchall()
    return [dict(row) for row in rows]


def get_lead(lead_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> dict[str, Any] | None:
    with _connect(db_path) as connection:
        row = connection.execute(
            "SELECT * FROM leads WHERE id = ?", (lead_id,)
        ).fetchone()
    return dict(row) if row is not None else None


def save_lead(
    lead: dict[str, Any],
    lead_id: int | None = None,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> int:
    """Insert a lead or update an existing lead, returning its id."""
    company_name = str(lead.get("company_name", "")).strip()
    if not company_name:
        raise ValueError("Company name is required.")

    values = {field: lead.get(field, "") for field in LEAD_FIELDS}
    values["company_name"] = company_name
    values["fit_score"] = values["fit_score"] or None

    with _connect(db_path) as connection:
        if lead_id is None:
            cursor = connection.execute(
                """
                INSERT INTO leads (
                    company_name, website, contact_name, job_title, email,
                    industry, location, research_notes, source_urls,
                    ai_summary, fit_score
                ) VALUES (
                    :company_name, :website, :contact_name, :job_title, :email,
                    :industry, :location, :research_notes, :source_urls,
                    :ai_summary, :fit_score
                )
                """,
                values,
            )
            return int(cursor.lastrowid)

        updated = connection.execute(
            """
            UPDATE leads SET
                company_name = :company_name,
                website = :website,
                contact_name = :contact_name,
                job_title = :job_title,
                email = :email,
                industry = :industry,
                location = :location,
                research_notes = :research_notes,
                source_urls = :source_urls,
                ai_summary = :ai_summary,
                fit_score = :fit_score,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
            """,
            {**values, "id": lead_id},
        )
        if updated.rowcount == 0:
            raise ValueError(f"Lead {lead_id} does not exist.")
    return lead_id


def delete_lead(lead_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as connection:
        deleted = connection.execute(
            "DELETE FROM leads WHERE id = ?", (lead_id,)
        )
        if deleted.rowcount == 0:
            raise ValueError(f"Lead {lead_id} does not exist.")
