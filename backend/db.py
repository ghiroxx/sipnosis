from datetime import datetime, timedelta, timezone

import psycopg2
from supabase import Client, create_client

from backend.config import (
    SUPABASE_DB_URL,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
)

GRACE_SECONDS_AFTER_HOUR = 8

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)


def get_supabase_client() -> Client:
    return supabase


def test_database_connection() -> bool:
    try:
        supabase.table("hour_questions").select("id").limit(1).execute()
        return True
    except Exception:
        return False


def run_simple_connection_check():
    if not SUPABASE_DB_URL:
        print("INFO: SUPABASE_DB_URL not configured.")
        return

    conn = psycopg2.connect(SUPABASE_DB_URL)
    conn.close()
    print("Database connection OK.")


def purge_expired_questions():
    cutoff = datetime.now(timezone.utc) - timedelta(
        seconds=GRACE_SECONDS_AFTER_HOUR
    )

    expired = (
        supabase.table("hour_questions")
        .select("id")
        .lt("expires_at", cutoff.isoformat())
        .execute()
        .data
        or []
    )

    if expired:
        ids = [row["id"] for row in expired]

        (
            supabase.table("hour_questions")
            .delete()
            .in_("id", ids)
            .execute()
        )
