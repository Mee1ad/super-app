-- Fix moods table schema to match the model
-- This script will ensure the moods table has the correct columns

-- Check if description column exists and remove it if it does
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'moods' AND column_name = 'description'
    ) THEN
        ALTER TABLE moods DROP COLUMN description;
        RAISE NOTICE 'Removed description column from moods table';
    ELSE
        RAISE NOTICE 'Description column does not exist in moods table';
    END IF;
END $$;

-- Ensure required columns exist
ALTER TABLE moods 
ADD COLUMN IF NOT EXISTS emoji VARCHAR(10),
ADD COLUMN IF NOT EXISTS color VARCHAR(20);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_moods_name ON moods(name); 