import sqlite3, json

db=r'C:\Users\yoeld\Documents\ChatGPT\TTIGRAAS Game\data\chronicles.db'
sess='ae9f071402b8f15fa16f0457d3521204'
conn=sqlite3.connect(db)
cur=conn.cursor()
cur.execute('select state_json from saves where session_id=?',(sess,))
row=cur.fetchone()
if not row:
    print('NOT FOUND')
else:
    obj=json.loads(row[0])
    print('FOUND, started=', obj.get('started'))
    print('keys:', list(obj.keys()))
conn.close()
