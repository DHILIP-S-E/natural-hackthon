-- Add google_id column to users table for Google OAuth support
-- Run this once against your PostgreSQL database:
--   psql $DATABASE_URL -f migrations/add_google_id.sql

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS google_id VARCHAR(128) UNIQUE;

CREATE INDEX IF NOT EXISTS ix_users_google_id ON users (google_id);
