import sqlite3, os
db=os.path.join(os.path.dirname(__file__),'data.db')
if os.path.exists(db):
    os.remove(db)
conn=sqlite3.connect(db); cur=conn.cursor()
cur.execute('CREATE TABLE citizens (id INTEGER PRIMARY KEY AUTOINCREMENT, national_id TEXT, full_name TEXT, dob TEXT)')
cur.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
cur.executemany('INSERT INTO citizens (national_id, full_name, dob) VALUES (?,?,?)', [
    ('435167851001','Abebe Mekonnen','1990-01-15'),
    ('435167851002','Lily Wondimu','1985-07-23'),
    ('435167851003','Samuel Tesfaye','1992-03-09'),
    ('435167851004','Hana Getachew','1978-11-30'),
    ('435167851005','Daniel Desta','1995-06-12'),
    ('435167851006','Sisay Mekonnen','1989-01-15'),
    ('435167851007','Ahmed Wase','1985-07-23'),
    ('435167851008','Sheferaw Girma','1992-03-09'),
    ('435167851009','Hanan Omer','1990-11-30'),
    ('435167851000','Ali Hussen','1995-06-12'),
])
cur.execute("INSERT INTO users (username,password) VALUES ('admin','202518')")
conn.commit(); conn.close()
print('seeded')
