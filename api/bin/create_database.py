import contextlib
import json
import sqlite3

DATABASE2 = './var/word_list.db'
DATABASE = './var/answers.db'
SCHEMA = './share/answers.sql'
file = open('../share/answers.json')
data = json.load(file)
with contextlib.closing(sqlite3.connect(DATABASE)) as db:
    with open(SCHEMA) as f:
        db.executescript(f.read())
        for word in data:
            while True:
                try:
                    # db.execute("""INSERT INTO words(word) VALUES(?)""", [word])
                    db.execute("""INSERT INTO answers(words) VALUES(?)""", [word])
                except sqlite3.IntegrityError:
                    continue
                break
        file.close()
        db.commit()
