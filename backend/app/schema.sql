CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS research_cache (
    cache_key text PRIMARY KEY, payload jsonb NOT NULL, expires_at timestamptz NOT NULL
);
CREATE TABLE IF NOT EXISTS monthly_usage (
    month date PRIMARY KEY, reserved integer NOT NULL CHECK (reserved >= 0)
);
CREATE TABLE IF NOT EXISTS provider_rate (
    provider text PRIMARY KEY, next_request timestamptz NOT NULL
);
CREATE TABLE IF NOT EXISTS sources (
    provider text NOT NULL, url text NOT NULL, pmid text, doi text,
    retrieved_at timestamptz NOT NULL, embedding vector,
    PRIMARY KEY (provider, url)
);
