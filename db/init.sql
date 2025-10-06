CREATE TABLE IF NOT EXISTS funding_digest_runs (
    id BIGSERIAL PRIMARY KEY,
    run_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_funding_digest_runs_created_at
    ON funding_digest_runs (created_at DESC);
