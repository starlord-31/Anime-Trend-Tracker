CREATE TABLE IF NOT EXISTS anime (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genre VARCHAR(255),
    rating DECIMAL(3, 1),
    synopsis TEXT,
    aired_start DATE,
    aired_end DATE,
    popularity INTEGER,
    type VARCHAR(50)
);
