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
INSERT INTO games VALUES(X'b34c5467bd33cd47a631a89cd3bcbabf',76791,8,'2022-03-08',6,1);
INSERT INTO games VALUES(X'2464b3a0cf8d5f4cb7805e974a75c716',40449,83,'2022-03-22',4,0);
INSERT INTO games VALUES(X'72e6e3fafe11954dba49c70a68f94a00',97653,34,'2022-01-06',3,1);
INSERT INTO games VALUES(X'7ebb6e9ad9eb3d4891c7b597ef6bf2a1',21987,2,'2022-01-07',2,1);
INSERT INTO games VALUES(X'c34bff64d5647148ab010dfe80796558',4122,69,'2022-03-22',3,1);
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
