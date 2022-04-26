PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE games(
    user_uuid GUID NOT NULL,
    user_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    finished DATE DEFAULT CURRENT_TIMESTAMP,
    guesses INTEGER,
    won BOOLEAN,
    PRIMARY KEY(game_id)
);
INSERT INTO games VALUES(X'575afea39b4e8c4fbd4dfdd47e732b24',21987,2,'2022-01-07',2,1);
INSERT INTO games VALUES(X'eb85986f8316e240987f816362241486',76791,8,'2022-03-08',6,1);
INSERT INTO games VALUES(X'6d1f149e4357d542a7b5ab0cb84d63f7',97653,34,'2022-01-06',3,1);
INSERT INTO games VALUES(X'93c7dc32e1015142929aadd893c3ea89',4122,69,'2022-03-22',3,1);
INSERT INTO games VALUES(X'1d1120a044d4614794b71fcf9bae3460',40449,83,'2022-03-22',4,0);
CREATE INDEX games_won_idx ON games(won);
CREATE VIEW wins
AS
    SELECT
        user_uuid,
        COUNT(won)
    FROM
        games
    WHERE
        won = TRUE
    GROUP BY
        user_uuid
    ORDER BY
        COUNT(won) DESC;
CREATE VIEW streaks
AS
    WITH ranks AS (
        SELECT DISTINCT
            user_uuid,
            finished,
            RANK() OVER(PARTITION BY user_uuid ORDER BY finished) AS rank
        FROM
            games
        WHERE
            won = TRUE
        ORDER BY
            user_uuid,
            finished
    ),
    groups AS (
        SELECT
            user_uuid,
            finished,
            rank,
            DATE(finished, '-' || rank || ' DAYS') AS base_date
        FROM
            ranks
    )
    SELECT
        user_uuid,
        COUNT(*) AS streak,
        MIN(finished) AS beginning,
        MAX(finished) AS ending
    FROM
        groups
    GROUP BY
        user_uuid, base_date
    HAVING
        streak > 1
    ORDER BY
        user_uuid,
        finished;
COMMIT;
