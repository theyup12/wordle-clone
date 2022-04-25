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
INSERT INTO games VALUES(X'd9bb925091e6794f9563d5109d27af44',69682,37,'2022-02-26',5,1);
INSERT INTO games VALUES(X'4126149cbd224d4797bce0debc941724',89791,82,'2022-02-10',1,1);
INSERT INTO games VALUES(X'9a4b06fcc9621d42ac0066e7ba1eeb5a',53152,9,'2022-02-23',3,1);
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
