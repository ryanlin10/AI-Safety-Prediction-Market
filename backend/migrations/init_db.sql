-- Initialize database with pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    handle VARCHAR(80) UNIQUE NOT NULL,
    email_hash VARCHAR(256) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sources table
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    url TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scraped TIMESTAMP
);

-- Ideas table
CREATE TABLE IF NOT EXISTS ideas (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    keywords TEXT[],
    embedding vector(1536),
    extracted_claim TEXT,
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS ideas_embedding_idx ON ideas USING ivfflat (embedding vector_cosine_ops);

-- Markets table
CREATE TABLE IF NOT EXISTS markets (
    id SERIAL PRIMARY KEY,
    idea_id INTEGER REFERENCES ideas(id),
    question_text TEXT NOT NULL,
    outcomes JSONB NOT NULL,
    resolution_rule JSONB,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    close_date TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_outcome VARCHAR(50),
    bid_price FLOAT,
    ask_price FLOAT
);

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    type VARCHAR(50) NOT NULL,
    creds JSONB,
    meta JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Bets table
CREATE TABLE IF NOT EXISTS bets (
    id SERIAL PRIMARY KEY,
    market_id INTEGER REFERENCES markets(id),
    user_id INTEGER REFERENCES users(id),
    agent_id INTEGER REFERENCES agents(id),
    outcome VARCHAR(50) NOT NULL,
    stake FLOAT NOT NULL,
    odds FLOAT NOT NULL,
    rationale TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Experiments table
CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    market_id INTEGER REFERENCES markets(id),
    agent_id INTEGER REFERENCES agents(id),
    config JSONB NOT NULL,
    result JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    logs TEXT,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ideas_source ON ideas(source_id);
CREATE INDEX IF NOT EXISTS idx_ideas_confidence ON ideas(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_markets_status ON markets(status);
CREATE INDEX IF NOT EXISTS idx_markets_idea ON markets(idea_id);
CREATE INDEX IF NOT EXISTS idx_bets_market ON bets(market_id);
CREATE INDEX IF NOT EXISTS idx_bets_agent ON bets(agent_id);
CREATE INDEX IF NOT EXISTS idx_experiments_market ON experiments(market_id);
CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status);

