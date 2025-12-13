from app.database import db

conn = db.conectar()
if not conn:
    print('No connection')
else:
    cursor = conn.cursor()
    cursor.execute('SELECT id, usuario, email, telefone FROM usuarios ORDER BY id DESC LIMIT 10')
    for r in cursor.fetchall():
        print(r)
    cursor.close()
    conn.close()