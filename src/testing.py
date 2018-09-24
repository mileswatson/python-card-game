import sqlite3 as sql
from hashlib import sha256

db = sql.connect("C:/Users/miles/Documents/Programming/python-card-game/testgame/users.dbf")

cursor = db.cursor()

cursor.execute("CREATE TABLE users(\
                    id          INTEGER PRIMARY KEY,\
                    username    TEXT,\
                    password    TEXT,\
                    best        INTEGER\
                )"
)

cursor.execute("INSERT INTO users(username,password,best) VALUES(?,?,?)",("DrWatson321",sha256(("DrWatson321Password01").encode()).digest(),1032))

#cursor.execute("SELECT * FROM users WHERE username=? AND password=?",("DrWatson321", "Password01"))
print(cursor.fetchall())

db.commit()
cursor.close()
db.close()