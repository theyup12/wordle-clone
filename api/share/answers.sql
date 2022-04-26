PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS answers
CREATE TABLE answers(
id INTEGER PRIMARY KEY,
words VARCHAR,
UNIQUE(words)
)
