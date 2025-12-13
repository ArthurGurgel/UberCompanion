from app import create_app
from app.models import User
from app.database import db

app = create_app()

with app.test_client() as c:
    # Create two users via model
    success1, msg1 = User.criar_usuario('userA', 'userA@example.com', '111', 'passA')
    success2, msg2 = User.criar_usuario('userB', 'userB@example.com', '222', 'passB')
    print('Create userA:', success1, msg1)
    print('Create userB:', success2, msg2)

    # Get their ids directly
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE email = %s", ('userA@example.com',))
    idA = cur.fetchone()[0]
    cur.execute("SELECT id FROM usuarios WHERE email = %s", ('userB@example.com',))
    idB = cur.fetchone()[0]
    cur.close()
    conn.close()

    # User A: set session and create records
    with c.session_transaction() as sess:
        sess['user'] = 'userA'
        sess['user_id'] = idA

    r1 = c.post('/api/abastecimentos', json={'custo': 100, 'custolt': 5.0, 'data': '12-12-2025'})
    print('/api/abastecimentos create A ->', r1.status_code, r1.json)
    r2 = c.post('/api/ganhos', json={'ganho': 200.0, 'kmrodado': 50, 'mediacar': 10, 'data': '12-12-2025'})
    print('/api/ganhos create A ->', r2.status_code, r2.json)

    # User B: set session and create records
    with c.session_transaction() as sess:
        sess['user'] = 'userB'
        sess['user_id'] = idB

    r3 = c.post('/api/abastecimentos', json={'custo': 150, 'custolt': 6.0, 'data': '12-12-2025'})
    print('/api/abastecimentos create B ->', r3.status_code, r3.json)
    r4 = c.post('/api/ganhos', json={'ganho': 300.0, 'kmrodado': 60, 'mediacar': 8, 'data': '12-12-2025'})
    print('/api/ganhos create B ->', r4.status_code, r4.json)

    # Now list gains as A
    with c.session_transaction() as sess:
        sess['user'] = 'userA'
        sess['user_id'] = idA

    r5 = c.get('/api/ganhos')
    print('GET /api/ganhos as A ->', r5.status_code, r5.json)
    r6 = c.get('/api/abastecimentos')
    print('GET /api/abastecimentos as A ->', r6.status_code, r6.json)

    # Now list gains as B
    with c.session_transaction() as sess:
        sess['user'] = 'userB'
        sess['user_id'] = idB

    r7 = c.get('/api/ganhos')
    print('GET /api/ganhos as B ->', r7.status_code, r7.json)
    r8 = c.get('/api/abastecimentos')
    print('GET /api/abastecimentos as B ->', r8.status_code, r8.json)
