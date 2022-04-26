import contextlib
import sqlite3
import uuid
DATABASE = './var/stats.db'
DATABASE_s1 = './var/stats_s1.db'
DATABASE_s2 = './var/stats_s2.db'
DATABASE_s3 = './var/stats_s3.db'
DATABASE_user = './var/user.db'
SCHEMA = './share/shard.sql'

NUM_USERS = 100_000
record_s1 = []
record_s2 = []
record_s3 = []
record_user = []

with contextlib.closing(sqlite3.connect(DATABASE)) as db:
    for row in db.execute("SELECT * FROM games LIMIT 20;"):
        if row[0] % 3 == 0:
            record_s1.append(row)
        elif row[0] % 3 == 1:
            record_s2.append(row)
        else:
            record_s3.append(row)
    for user in db.execute("SELECT * FROM users"):
        record_user.append(user)
# user table have user name, id, and uuid
# game table have user id, game id, uuid match to user table and other stay the same.
sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)

conn = sqlite3.connect(DATABASE_user, detect_types=sqlite3.PARSE_DECLTYPES)
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS users;")
c.execute("""CREATE TABLE users(
    user_uuid GUID PRIMARY KEY,
    user_id INTEGER,
    username VARCHAR UNIQUE
    );""")
for row in record_user:
    data = (uuid.uuid4(), row[0], row[1])
    c.execute("""INSERT INTO users(user_uuid, user_id, username) VALUES(?, ?, ?)""", data)

conn.commit()

# game = VALUES(user_id, game_id,'2022-03-03', guesses = 4, won = 0)
with contextlib.closing(sqlite3.connect(DATABASE_s1)) as db:
    with open(SCHEMA) as f:
        db.executescript(f.read())

    db.execute("ATTACH './var/user.db' as Users")
    for row in record_s1:
        while True:
            try:
                cur = db.execute("SELECT user_uuid FROM Users.users WHERE Users.users.user_id = ?", [row[0]])
                uid = cur.fetchone()[0]
                data = (uid, row[0], row[1], row[2], row[3], row[4])
                db.execute("""
                            INSERT INTO games(user_uuid, user_id, game_id, finished, guesses, won)
                            VALUES(?, ?, ?, ?, ?, ?)
                            """, data)
            except sqlite3.IntegrityError:
                continue
            break
    db.commit()

with contextlib.closing(sqlite3.connect(DATABASE_s2)) as db:
    with open(SCHEMA) as f:
        db.executescript(f.read())

    db.execute("ATTACH './var/user.db' as Users")
    for row in record_s2:
        while True:
            try:
                cur = db.execute("SELECT user_uuid FROM Users.users WHERE Users.users.user_id = ?", [row[0]])
                uid = cur.fetchone()[0]
                data = (uid, row[0], row[1], row[2], row[3], row[4])
                db.execute("""
                            INSERT INTO games(user_uuid, user_id, game_id, finished, guesses, won)
                            VALUES(?, ?, ?, ?, ?, ?)
                            """, data)
            except sqlite3.IntegrityError:
                continue
            break
    db.commit()

with contextlib.closing(sqlite3.connect(DATABASE_s3)) as db:
    with open(SCHEMA) as f:
        db.executescript(f.read())

    db.execute("ATTACH './var/user.db' as Users")
    for row in record_s3:
        while True:
            try:
                cur = db.execute("SELECT user_uuid FROM Users.users WHERE Users.users.user_id = ?", [row[0]])
                uid = cur.fetchone()[0]
                data = (uid, row[0], row[1], row[2], row[3], row[4])
                db.execute("""
                            INSERT INTO games(user_uuid, user_id, game_id, finished, guesses, won)
                            VALUES(?, ?, ?, ?, ?, ?)
                            """, data)
            except sqlite3.IntegrityError:
                continue
            break
    db.commit()
