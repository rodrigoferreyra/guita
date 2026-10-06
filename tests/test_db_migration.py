"""Regression: existing DBs migrate to the alias column safely."""

from pathlib import Path

from guita.app.service import GuitaService
from guita.persistence.db import connect, initialize_db


def test_migrate_existing_db_without_alias_column(tmp_path: Path) -> None:
    db_path = tmp_path / "legacy.db"
    conn = connect(db_path)
    conn.executescript(
        """
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            currency TEXT NOT NULL DEFAULT 'USD',
            created_at TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        );
        CREATE UNIQUE INDEX idx_accounts_name_lower ON accounts (lower(name));
        INSERT INTO accounts (name, currency, created_at, active)
        VALUES ('Wise', 'USD', '2026-01-01T00:00:00+00:00', 1);
        """
    )
    conn.commit()
    conn.close()

    # Opening through the service must migrate, not crash.
    with GuitaService(db_path) as svc:
        accounts = svc.list_accounts()
        assert len(accounts) == 1
        assert accounts[0].name == "Wise"
        assert accounts[0].alias is None
        wisdom = svc.add_account("Wisdom", alias="wdm")
        assert wisdom.alias == "wdm"

    # Second open stays healthy.
    conn = connect(db_path)
    initialize_db(conn)
    columns = {str(row["name"]) for row in conn.execute("PRAGMA table_info(accounts)")}
    assert "alias" in columns
    conn.close()
