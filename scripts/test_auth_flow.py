from app import create_app

app = create_app()

with app.test_client() as c:
    # Test GET login page
    r = c.get('/')
    print('GET / ->', r.status_code)

    # Test GET cadastro page
    r2 = c.get('/cadastro')
    print('GET /cadastro ->', r2.status_code)

    # Try to register a new user (use a unique email to avoid duplicate error)
    import random
    suffix = random.randint(10000,99999)
    data = {
        'usuario': f'testuser{suffix}',
        'email': f'test{suffix}@example.com',
        'telefone': '999999999',
        'senha': 'senha123'
    }
    r3 = c.post('/cadastro', data=data, follow_redirects=True)
    print('POST /cadastro ->', r3.status_code)
    print(r3.data.decode()[:400])

    # Try to login with same credentials
    r4 = c.post('/login', data={'usuario': data['email'], 'senha': data['senha']}, follow_redirects=True)
    print('POST /login ->', r4.status_code)
    print(r4.data.decode()[:400])

    # Now create a ganho and abastecimento for this user via API
    ganho_payload = {'ganho': 100.0, 'kmrodado': 50, 'mediacar': 10, 'data': '12-12-2025'}
    r5 = c.post('/api/ganhos', json=ganho_payload)
    print('POST /api/ganhos ->', r5.status_code, r5.json)

    abastecimento_payload = {'custo': 200.0, 'custolt': 5.0, 'data': '12-12-2025'}
    r6 = c.post('/api/abastecimentos', json=abastecimento_payload)
    print('POST /api/abastecimentos ->', r6.status_code, r6.json)

    # Now register another user and ensure they don't see first user's ganhos
    suffix2 = random.randint(100000,199999)
    data2 = {
        'usuario': f'testuser{suffix2}',
        'email': f'test{suffix2}@example.com',
        'telefone': '88888888',
        'senha': 'senha123'
    }
    r7 = c.post('/cadastro', data=data2, follow_redirects=True)
    r8 = c.post('/login', data={'usuario': data2['email'], 'senha': data2['senha']}, follow_redirects=True)
    print('Login user2 ->', r8.status_code)

    # user2 listar ganhos -> should be empty or not include user1's item
    r9 = c.get('/api/ganhos')
    print('GET /api/ganhos after login user2 ->', r9.status_code, r9.json)

    # Check dashboard values for user1 and user2 isolation
    # Log back as user1
    r10 = c.post('/login', data={'usuario': data['email'], 'senha': data['senha']}, follow_redirects=True)
    r11 = c.get('/api/dashboard')
    print('User1 /api/dashboard ->', r11.status_code, r11.json)

    # Login back as user2
    r12 = c.post('/login', data={'usuario': data2['email'], 'senha': data2['senha']}, follow_redirects=True)
    r13 = c.get('/api/dashboard')
    print('User2 /api/dashboard ->', r13.status_code, r13.json)
