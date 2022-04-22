import contextlib
import sqlite3

DATABASE = './var/stats.db'
DATABASE_s1 = './var/stats_s1.db'
DATABASE_s2 = './var/stats_s2.db'
DATABASE_s3 = './var/stats_s3.db'
DATABASE_s4 = './var/user.db'
SCHEMA = './share/shard.sql'

record_s1 = []
record_s2 = []
record_s3 = []
with contextlib.closing(sqlite3.connect(DATABASE)) as db:
    for row in db.execute("SELECT * FROM games LIMIT 10 "):
        if row[0] % 3 == 0:
            record_s1.append(row)
        elif row[0] % 3 == 1:
            record_s2.append(row)
        else:
            record_s3.append(row)
