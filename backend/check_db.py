import sqlite3
conn = sqlite3.connect('solar_prediction.db')
c = conn.cursor()
tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', tables)
for t in tables:
    count = c.execute('SELECT COUNT(*) FROM ' + t[0]).fetchone()[0]
    print(t[0], count)
conn.close()
