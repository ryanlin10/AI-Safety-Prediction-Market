-- Add bid_price and ask_price columns to markets table
-- This migration adds columns to store the initial bid/ask prices from markets.json

-- For SQLite:
ALTER TABLE markets ADD COLUMN bid_price REAL;
ALTER TABLE markets ADD COLUMN ask_price REAL;

-- For PostgreSQL (if needed):
-- ALTER TABLE markets ADD COLUMN IF NOT EXISTS bid_price FLOAT;
-- ALTER TABLE markets ADD COLUMN IF NOT EXISTS ask_price FLOAT;

