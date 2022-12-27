import sqlite3

db = sqlite3.connect("db.sqlite3")
db.cursor().execute("drop table if exists users")
db.cursor().execute("drop table if exists messages")
db.cursor().execute("create table users (id INTEGER primary key autoincrement, username text unique, password text);")
db.cursor().execute(
"""
create table messages (
    id INTEGER primary key autoincrement,
    sender_id INTEGER references users(id),
    receiver_id INTEGER references users(id),
    title TEXT,
    content TEXT
    )
""")

db.cursor().execute("insert into users (username, password) values ('John', 'd41e98d1eafa6d6011d3a70f1a5b92f0')")
db.cursor().execute("insert into users (username, password) values ('admin', 'e3afed0047b08059d0fada10f400c1e5')")
db.cursor().execute("insert into users (username, password) values ('Mary', 'ee7f55af2afd5bf7fabd52f36812d0e3')")
db.commit()

"""
Passwords:

John
Passw0rd

admin
Admin

Mary
HadACow
"""