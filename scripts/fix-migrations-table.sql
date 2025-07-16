-- Fix migrations table schema
-- This script will recreate the migrations table with the correct schema

-- Drop the existing migrations table if it exists
DROP TABLE IF EXISTS migrations;

-- Create the migrations table with the correct schema
CREATE TABLE migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    dependencies TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on version for faster lookups
CREATE INDEX idx_migrations_version ON migrations(version);

-- Create index on applied_at for status queries
CREATE INDEX idx_migrations_applied_at ON migrations(applied_at); 