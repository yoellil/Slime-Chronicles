import sqlite3
db = r'C:\Users\yoeld\Documents\ChatGPT\TTIGRAAS Game\data\chronicles.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute('SELECT session_id, length(state_json) FROM saves')
rows = cur.fetchall()
for r in rows:
    print('SESSION:', r[0], 'LEN:', r[1])
conn.close()