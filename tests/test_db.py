from backend.db import test_database_connection


def test_db_function_exists():
    result = test_database_connection()
    assert isinstance(result, bool)
