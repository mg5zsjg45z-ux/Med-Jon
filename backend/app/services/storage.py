import os
import hashlib
import json
from datetime import datetime, timezone
import psycopg

def connect():
    return psycopg.connect(os.environ["DATABASE_URL"])

def key_for(source, value):
    return hashlib.sha256(f"{source}:{value}".encode()).hexdigest()

def initialize():
    with connect() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute("""CREATE TABLE IF NOT EXISTS evidence_cache (
            key text PRIMARY KEY, payload jsonb NOT NULL,
            expires_at timestamptz NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS credit_budget (
            period text PRIMARY KEY, reserved integer NOT NULL CHECK (reserved >= 0))""")

def get_cached(key):
    with connect() as conn:
        row = conn.execute("SELECT payload FROM evidence_cache WHERE key=%s AND expires_at>now()", (key,)).fetchone()
        return row[0] if row else None

def put_cached(key, payload, hours=168):
    with connect() as conn:
        conn.execute("""INSERT INTO evidence_cache VALUES (%s,%s::jsonb,now()+%s*interval '1 hour')
            ON CONFLICT(key) DO UPDATE SET payload=excluded.payload, expires_at=excluded.expires_at""",
            (key,json.dumps(payload),hours))

def reserve_credits(amount=1):
    # Conservative local reservation, not a provider billing guarantee.
    limit = int(os.getenv("FIRECRAWL_MONTHLY_BUDGET", "800"))
    if amount <= 0 or amount > limit:
        return False
    period = datetime.now(timezone.utc).strftime("%Y-%m")
    with connect() as conn:
        row = conn.execute("""INSERT INTO credit_budget VALUES (%s,%s)
            ON CONFLICT(period) DO UPDATE SET reserved=credit_budget.reserved+excluded.reserved
            WHERE credit_budget.reserved+excluded.reserved<=%s RETURNING reserved""",
            (period,amount,limit)).fetchone()
        return row is not None
