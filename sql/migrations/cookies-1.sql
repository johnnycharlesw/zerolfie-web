-- Migration script to update the `cookies` table to the new schema

-- Step 1: Add new columns with default values or NULL as appropriate
ALTER TABLE cookies ADD COLUMN domain TEXT NOT NULL DEFAULT 'localhost';
ALTER TABLE cookies ADD COLUMN expires DATETIME NOT NULL DEFAULT (datetime('now', '+1 year'));
ALTER TABLE cookies ADD COLUMN same_site TEXT CHECK (same_site IN ('Strict', 'Lax', 'None')) DEFAULT 'Lax';

-- Step 2: Update existing rows to ensure NOT NULL constraints are satisfied
UPDATE cookies SET domain = 'example.com' WHERE domain IS NULL;
UPDATE cookies SET expires = datetime('now', '+1 year') WHERE expires IS NULL;
UPDATE cookies SET same_site = 'Lax' WHERE same_site IS NULL;

-- Step 3: Add CHECK constraints for the new columns (if not already handled by ALTER TABLE)
-- (SQLite does not support adding CHECK constraints via ALTER TABLE after column creation, so this is informational)
-- Ensure application logic enforces these constraints for new data.

-- Optional: Add indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_cookies_name ON cookies(name);
CREATE INDEX IF NOT EXISTS idx_cookies_domain ON cookies(domain);
CREATE INDEX IF NOT EXISTS idx_cookies_expires ON cookies(expires);
