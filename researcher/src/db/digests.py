from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json

from src.setup import settings
from src.types import StartupFundingSearchEngineOutput

_LOGGER = logging.getLogger("startup_researcher.db.digests")


def _get_connection() -> psycopg.Connection:
    if not settings.DATABASE_URL:
        msg = "DATABASE_URL is not configured."
        raise RuntimeError(msg)
    return psycopg.connect(settings.DATABASE_URL, row_factory=dict_row)


def _insert_digest(
    result: StartupFundingSearchEngineOutput,
    run_id: Optional[str] = None,
    recorded_at: Optional[datetime] = None,
) -> str:
    payload = result.model_dump(mode="json")
    run_identifier = run_id or str(uuid.uuid4())
    recorded_ts = recorded_at.astimezone(timezone.utc) if recorded_at else datetime.now(timezone.utc)

    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO funding_digest_runs (run_id, created_at, data)
                VALUES (%s, %s, %s::jsonb)
                ON CONFLICT (run_id) DO UPDATE
                SET created_at = EXCLUDED.created_at,
                    data = EXCLUDED.data
                RETURNING run_id
                """,
                (run_identifier, recorded_ts, Json(payload)),
            )
            returned = cur.fetchone()
        conn.commit()

    _LOGGER.info("Stored digest run %s", run_identifier)
    return returned["run_id"] if isinstance(returned, dict) else run_identifier


async def insert_digest(
    result: StartupFundingSearchEngineOutput,
    run_id: Optional[str] = None,
    recorded_at: Optional[datetime] = None,
) -> str:
    return await asyncio.to_thread(_insert_digest, result, run_id, recorded_at)


__all__ = ["insert_digest"]
