--- SQLITE DIALECT ---

CREATE TABLE IF NOT EXISTS messages (
    platform TEXT NOT NULL,
    id TEXT NOT NULL,
    at TEXT NOT NULL,
    message TEXT NOT NULL,
    PRIMARY KEY (platform, id)
)