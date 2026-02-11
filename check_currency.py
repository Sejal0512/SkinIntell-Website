import sqlite3

conn = sqlite3.connect('skinintel.db')
cursor = conn.cursor()
cursor.execute('SELECT name, price FROM Products LIMIT 5')
products = cursor.fetchall()
print("First 5 products:")
for p in products:
    print(f"{p[0]}: {p[1]}")
conn.close()
