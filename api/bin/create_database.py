import contextlib
import json
import sqlite3

DATABASE = '../var/answers.db'
SCHEMA = '../share/answers.sql'
file = open('../share/answers.json')
data = json.load(file)
with contextlib.closing(sqlite3.connect(DATABASE)) as db:
    with open(SCHEMA) as f:
        db.executescript(f.read())
        for word in data:
            db.execute("""INSERT INTO answers(words) VALUES(?)""", [word])
        file.close()
        db.commit()

