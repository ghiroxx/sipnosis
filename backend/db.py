from datetime import datetime, timedelta, timezone

try:
    import psycopg2
except Exception:  # pragma: no cover - optional runtime dependency
    psycopg2 = None

try:
    from supabase import create_client
except Exception:  # pragma: no cover - optional runtime dependency
    create_client = None

from backend.config import (
    SUPABASE_DB_URL,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
)

GRACE_SECONDS_AFTER_HOUR = 8

_supabase = None


def get_supabase_client():
    global _supabase

    if _supabase is not None:
        return _supabase

    if not create_client or not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return None

    _supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _supabase


def test_database_connection() -> bool:
    client = get_supabase_client()

    if client is None:
        return False

    try:
        client.table("hour_questions").select("id").limit(1).execute()
        return True
    except Exception:
        return False


def run_simple_connection_check():
    if not SUPABASE_DB_URL:
        print("INFO: SUPABASE_DB_URL not configured.")
        return

    if psycopg2 is None:
        print("INFO: psycopg2 not installed; skipping direct DB check.")
        return

    conn = psycopg2.connect(SUPABASE_DB_URL)
    conn.close()
    print("Database connection OK.")


def purge_expired_questions():
    client = get_supabase_client()

    if client is None:
        return

    cutoff = datetime.now(timezone.utc) - timedelta(
        seconds=GRACE_SECONDS_AFTER_HOUR
    )

    expired = (
        client.table("hour_questions")
        .select("id")
        .lt("expires_at", cutoff.isoformat())
        .execute()
        .data
        or []
    )

    if expired:
        ids = [row["id"] for row in expired]

        (
            client.table("hour_questions")
            .delete()
            .in_("id", ids)
            .execute()
        )
