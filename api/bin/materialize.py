import contextlib
import sqlite3
import uuid
import redis
# from crontab import CronTab
# from pathlib import Path
DATABASE = '../var/stats.db'
DATABASE_s1 = '../var/stats_s1.db'
DATABASE_s2 = '../var/stats_s2.db'
DATABASE_s3 = '../var/stats_s3.db'
DATABASE_user = '../var/user.db'

cli = redis.Redis(host="localhost", port=6379)

# crontab -e
# */10 * * * * cd /home/student/wordle-project3/api/bin/ && /usr/bin/python3 materialize.py >> check.log
# crontab -l
print("executed")
# get views from the game table and convert into redis database

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
tables = [("wins", "count_wins"), ("streaks", "streak")]

for table in tables:
    with contextlib.closing(sqlite3.connect(DATABASE_user)) as db:
        db.execute("ATTACH '../var/stats_s1.db' as stats_s1")
        db.execute("ATTACH '../var/stats_s2.db' as stats_s2")
        db.execute("ATTACH '../var/stats_s3.db' as stats_s3")
        top_users_s1 = db.execute(f"""
        SELECT username, {table[1]}
        FROM stats_s1.{table[0]}
        INNER JOIN users ON users.user_uuid = stats_s1.{table[0]}.user_uuid
        ORDER BY {table[1]} DESC LIMIT 10;
        """)
        res = top_users_s1.fetchall()
        top_users_s2 = db.execute(f"""
        SELECT username, {table[1]}
        FROM stats_s2.{table[0]}
        INNER JOIN users ON users.user_uuid = stats_s2.{table[0]}.user_uuid
        ORDER BY {table[1]} DESC LIMIT 10;
        """)
        res += top_users_s2.fetchall()
        top_users_s3 = db.execute(f"""
        SELECT username, {table[1]}
        FROM stats_s3.{table[0]}
        INNER JOIN users ON users.user_uuid = stats_s3.{table[0]}.user_uuid
        ORDER BY {table[1]} DESC LIMIT 10;
        """)
        res += top_users_s3.fetchall()
        with cli.pipeline() as pipe:
            pipe.multi()
            cur_key = f"Top-{table[0]}"
            for user in res:
                cli.zadd(cur_key, {user[0]: user[1]})
            pipe.execute()
    pipe.close()

print("finished")
print(cli.zrevrange("Top-wins", 0, -1, withscores=True))
print(" ")
print(cli.zrevrange("Top-streaks", 0, -1, withscores=True))
