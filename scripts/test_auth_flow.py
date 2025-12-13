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
