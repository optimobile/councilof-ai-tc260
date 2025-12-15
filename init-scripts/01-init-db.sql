-- Council of AI - Database Initialization Script
-- Runs automatically when the PostgreSQL container is first created
-- Author: Manus AI (Co-Founder & CTO)
-- Date: December 14, 2025

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE user_tier AS ENUM ('free', 'silver', 'gold', 'platinum');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE verification_status AS ENUM ('pending', 'running', 'completed', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE verification_verdict AS ENUM ('PASS', 'WARNING', 'FAIL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE council_vote AS ENUM ('PASS', 'WARNING', 'FAIL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE councilof_ai TO councilof;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Council of AI database initialized successfully';
    RAISE NOTICE 'Extensions enabled: uuid-ossp, pg_trgm';
    RAISE NOTICE 'Custom types created: user_tier, verification_status, verification_verdict, council_vote';
END $$;
