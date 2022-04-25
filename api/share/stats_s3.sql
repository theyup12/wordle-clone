PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE games(
    user_uuid GUID NOT NULL,
    user_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    finished DATE DEFAULT CURRENT_TIMESTAMP,
    guesses INTEGER,
    won BOOLEAN,
    PRIMARY KEY(game_id, user_uuid)
);
INSERT INTO games VALUES(X'76f1263ab9e50a4699fda478f2dfd577',55130,9,'2022-03-29',1,0);
INSERT INTO games VALUES(X'd75a5c4a88634844b4c7250e15076ba0',73613,50,'2022-03-22',4,1);
CREATE INDEX games_won_idx ON games(won);
CREATE VIEW wins
AS
    SELECT
        user_id,
        COUNT(won)
    FROM
        games
    WHERE
        won = TRUE
    GROUP BY
        user_id
    ORDER BY
        COUNT(won) DESC;
CREATE VIEW streaks
AS
    WITH ranks AS (
        SELECT DISTINCT
            user_id,
            finished,
            RANK() OVER(PARTITION BY user_id ORDER BY finished) AS rank
        FROM
            games
        WHERE
            won = TRUE
        ORDER BY
            user_id,
            finished
    ),
    groups AS (
        SELECT
            user_id,
            finished,
            rank,
            DATE(finished, '-' || rank || ' DAYS') AS base_date
        FROM
            ranks
    )
    SELECT
        user_id,
        COUNT(*) AS streak,
        MIN(finished) AS beginning,
        MAX(finished) AS ending
    FROM
        groups
    GROUP BY
        user_id, base_date
    HAVING
        streak > 1
    ORDER BY
        user_id,
        finished;
COMMIT;
