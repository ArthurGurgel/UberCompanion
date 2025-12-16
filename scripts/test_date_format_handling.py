from app import create_app
from datetime import date

app = create_app()

def today_br_slash():
    hoje = date.today()
    return f"{hoje.day:02d}/{hoje.month:02d}/{hoje.year}"

with app.test_client() as c:
    # create a temporary user
    import random
    suffix = random.randint(100000,999999)
    user = {
        'usuario': f'testdate{suffix}',
        'email': f'testdate{suffix}@example.com',
        'telefone': '99999999',
        'senha': 'senha123'
    }
    r = c.post('/cadastro', data=user)

    # login
    r = c.post('/login', data={'usuario': user['email'], 'senha': user['senha']}, follow_redirects=True)
    print('Login status:', r.status_code)

    # create ganho using dd/mm/YYYY format
    today_slash = today_br_slash()
    ganho_payload = {'ganho': 150.0, 'kmrodado': 50, 'mediacar': 10, 'data': today_slash}
    r2 = c.post('/api/ganhos', json=ganho_payload)
    print('POST /api/ganhos ->', r2.status_code, r2.json)

    # Fetch dashboard
    r3 = c.get('/api/dashboard')
    print('GET /api/dashboard ->', r3.status_code, r3.json)
    ultimos = r3.json.get('ultimos_ganhos', [])
    print('Dates in ultimos_ganhos:', [g['data'] for g in ultimos])
    # Verify today's record present and normalized to dd-mm-YYYY
    expected_norm = today_slash.replace('/', '-')
    found = any(g['data'] == expected_norm for g in ultimos)
    print('Found normalized date:', found)
    print('Total semana reported:', r3.json.get('total_semana_atual'))
