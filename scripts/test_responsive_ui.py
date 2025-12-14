from app import create_app

app = create_app()

with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['user'] = 'tester'
        sess['user_id'] = 1

    r = c.get('/app')
    html = r.data.decode()
    print('GET /app ->', r.status_code)
    print('Has sidebar toggle:', 'id="sidebar-toggle"' in html)
    print('Includes sidebar.js:', 'sidebar.js' in html)
    print('Has semanas-chart canvas:', 'id="semanas-chart"' in html)
    print('Has ganhos-chart canvas:', 'id="ganhos-chart"' in html)
