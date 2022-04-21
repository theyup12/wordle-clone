import contextlib
import sqlite3

DATABASE = './var/stats.db'
DATABASE_s1 = './var/stats_s1.db'
DATABASE_s2 = './var/stats_s2.db'
DATABASE_s3 = './var/stats_s3.db'
SCHEMA = './share/shard.sql'

with contextlib.closing(sqlite3.connect(DATABASE)) as db:
   db.execute("ATTACH DATABASE ? AS stats_s1", [DATABASE_s1])
   db.execute("DROP TABLE IF EXISTS games;")
   db.execute("""
       CREATE TABLE stats_s1.games(
       game_id INTEGER NOT NULL PRIMARY KEY,
       finished DATE DEFAULT CURRENT_TIMESTAMP,
       guesses INTEGER,
       won BOOLEAN
       )""")
   db.execute("INSERT INTO stats_s1.games SELECT game_id, finished, guesses, won FROM games;")
   db.commit()
