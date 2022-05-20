import contextlib
import sqlite3
import uuid
import os.path
DATABASE = '../var/stats_v1.db'
DATABASE_s1 = '../var/stats_s1_v1.db'
DATABASE_s2 = '../var/stats_s2_v2.db'
DATABASE_s3 = '../var/stats_s3_v3.db'
DATABASE_user = '../var/user_v1.db'
SCHEMA = '../share/shard.sql'

NUM_USERS = 100_000
record_s1 = []
record_s2 = []
record_s3 = []
record_user = []

with contextlib.closing(sqlite3.connect(DATABASE)) as db:
    # for row in db.execute("SELECT * FROM games"):
    #     if row[0] % 3 == 0:
    #         record_s1.append(row)
    #     elif row[0] % 3 == 1:
    #         record_s2.append(row)
    #     else:
    #         record_s3.append(row)
    for user in db.execute("SELECT * FROM users"):
        record_user.append(user)
    # print(record_s1)
# user table have user name, id, and uuid
# game table have user id, game id, uuid match to user table and other stay the same.
sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: memoryview(u.bytes_le))

conn = sqlite3.connect(DATABASE_user, detect_types=sqlite3.PARSE_DECLTYPES)
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS users;")
c.execute("""CREATE TABLE users(
    user_uuid GUID PRIMARY KEY,
    user_id INTEGER,
    username VARCHAR UNIQUE
    );""")
user_id_dict = {}
for row in record_user:
    a_uuid = uuid.uuid4()
    user_id_dict[row[0]] = a_uuid
    data = (uuid.uuid4(), row[0], row[1])
    c.execute("""INSERT INTO users(user_uuid, user_id, username) VALUES(?, ?, ?)""", data)
conn.commit()
with contextlib.closing(sqlite3.connect(DATABASE)) as db1:
#     db1.execute("ATTACH '../var/user_v1.db' as user")
# # c.execute("ALTER TABLE stats.games ADD user_uuid GUID")
#     print("Adding uuid column to games table")
    the_tuples = []
    db1.execute("SELECT * FROM games")
    the_tuples.append(c.fetchone())
    print(the_tuples)
# for t in the_tuples:
#     c.execute("UPDATE stats.games SET user_uuid = ? WHERE user_id = ?", [user_id_dict[t[0]], t[0]])
# print("Updated Column Values")
# conn.commit()
#
# sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
# sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
# con1 = sqlite3.connect("../var/stats_v1.db", detect_types=sqlite3.PARSE_DECLTYPES)
# cur1 = con1.cursor()
# for i in range(3):
#     file_exists = os.path.exists(f"../var/stats_s1_v{i + 1}.db")
#     con2 = sqlite3.connect(f"../var/stats_s1_v{i + 1}.db", detect_types=sqlite3.PARSE_DECLTYPES)
#     cur2 = con2.cursor()
#     cur1.execute("SELECT * FROM games WHERE user_uuid % 3 = ?", [i])
#     list1 = cur1.fetchall()
#     if not file_exists:
#         with open(SCHEMA) as f:
#             cur2.executescript(f.read())
#         cur2.executemany("INSERT INTO games VALUES(?, ?, ?, ?, ?, ?)", list1)
#         con2.commit()
#         print(f"Shard {i + 1}: made")
#         con2.commit()
#     else:
#         print("DB already made")
#         con2.close()
