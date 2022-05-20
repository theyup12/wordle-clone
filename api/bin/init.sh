#!/bin/sh

sqlite3 ../var/stats.db < ./Database/populated.sql
python3 create_words_db.py
python3 create_database.py
python3 shard.py
