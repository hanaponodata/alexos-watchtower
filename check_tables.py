#!/usr/bin/env python3
"""Check database tables."""

from database.engine import get_engine_for_migrations
from sqlalchemy import text

engine = get_engine_for_migrations()
with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result]
    print(f"Tables: {tables}") 