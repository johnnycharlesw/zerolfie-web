CREATE TABLE IF NOT EXISTS cookies (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    `name` TEXT NOT NULL,
    `value` TEXT NULL,
    `path` TEXT NOT NULL,
    `flavor` TEXT CHECK (flavor IN ('HttpOnly', 'JavaScript', 'Both')) DEFAULT 'Both',
    `domain` TEXT NOT NULL,
    `expires` DATETIME NOT NULL,
    `same_site` TEXT CHECK (same_site IN ('Strict', 'Lax', 'None'))
);