"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from guita.app.service import GuitaService


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test-guita.db"


@pytest.fixture
def svc(db_path: Path) -> GuitaService:
    service = GuitaService(db_path)
    yield service
    service.close()


@pytest.fixture
def funded(svc: GuitaService) -> GuitaService:
    svc.add_account("Wise", "USD")
    svc.add_account("Wallbit", "USD")
    svc.add_money("1000", "Wise")
    return svc