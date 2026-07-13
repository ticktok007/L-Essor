-- Campus Innovation & Engagement Intelligence Hub
-- Enable pgvector on first container startup.

CREATE EXTENSION IF NOT EXISTS vector;

-- Verify: SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
