PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE games(
    user_uuid GUID,
    user_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    finished DATE DEFAULT CURRENT_TIMESTAMP,
    guesses INTEGER,
    won BOOLEAN,
    PRIMARY KEY(game_id)
);
INSERT INTO games VALUES(X'480c69af87c50c41a3c27e6725ef803c',21987,2,'2022-01-07',2,1);
INSERT INTO games VALUES(X'21447f591e17a64da4239fee860979a9',76791,8,'2022-03-08',6,1);
INSERT INTO games VALUES(X'aeaad46cae19184fb1d62f867afb4018',97653,34,'2022-01-06',3,1);
INSERT INTO games VALUES(X'beb421f3d25fa5499d2b63009143f970',4122,69,'2022-03-22',3,1);
INSERT INTO games VALUES(X'61547713719fce4ea86f7fd1603f8c73',40449,83,'2022-03-22',4,0);
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
