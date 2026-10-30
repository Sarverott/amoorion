--- SQLITE DIALECT ---

CREATE TABLE IF NOT EXISTS handled (
    rule TEXT NOT NULL, 
    platform TEXT NOT NULL, 
    id TEXT NOT NULL, 
    PRIMARY KEY (rule, platform, id)
)