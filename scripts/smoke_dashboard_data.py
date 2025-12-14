import json
from app import create_app

app = create_app()

with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['user'] = 'tester'
        sess['user_id'] = 1

    r = c.get('/api/dashboard')
    print('GET /api/dashboard ->', r.status_code)
    try:
        data = r.get_json()
        ganhos = data.get('ultimos_ganhos', [])
        print('Received ultimos_ganhos count:', len(ganhos))
        for g in ganhos[:10]:
            print('-', g.get('data'), 'lucro:', g.get('lucro'))
    except Exception as e:
        print('Error parsing JSON:', e)
