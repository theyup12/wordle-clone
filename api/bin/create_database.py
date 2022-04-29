import contextlib
import json
import sqlite3

DATABASE2 = '../var/word_list.db'
DATABASE = '../var/answers.db'
SCHEMA = '../share/answers.sql'
SCHEMA1 = '../share/words.sql'
file = open('../share/answers.json')
data = json.load(file)
with contextlib.closing(sqlite3.connect(DATABASE)) as db:
    with open(SCHEMA) as f:
        db.executescript(f.read())
        for word in data:
            db.execute("""INSERT INTO answers(words) VALUES(?)""", [word])
        file.close()
        db.commit()
file = open('../share/answers.json')
data = json.load(file)
with contextlib.closing(sqlite3.connect(DATABASE2)) as db:
    with open(SCHEMA1) as f:
        db.executescript(f.read())
        for word in data:
            db.execute("""INSERT INTO words(word) VALUES(?)""", [word])
        file.close()
        db.commit()
