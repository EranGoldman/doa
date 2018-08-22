import sqlite3
from flask import g
import os

DATABASE = 'db/database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    if "insert" in query:
        db.commit()
        cur.close()
        return
    else:
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
