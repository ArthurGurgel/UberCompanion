from app import create_app

app = create_app()

with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['user'] = 'tester'
        sess['user_id'] = 1

    r = c.get('/app')
    html = r.data.decode()
    print('GET /app ->', r.status_code)
    print('Has semanas-chart:', 'id="semanas-chart"' in html)
    print('Old pie-chart gone:', 'id="pie-chart"' not in html)
