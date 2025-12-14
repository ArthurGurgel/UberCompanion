from app import create_app

app = create_app()

with app.test_client() as c:
    # Simulate logged-in user by setting session
    with c.session_transaction() as sess:
        sess['user'] = 'tester'
        sess['user_id'] = 42

    r = c.get('/app')
    print('GET /app ->', r.status_code)
    html = r.data.decode()
    print('Contains Perfil:', 'Perfil' in html)
    print('Contains Sair:', 'Sair' in html)
    # Print small snippet around nav
    start = html.find('<nav class="nav-menu">')
    print(html[start:start+400])
    # Now call logout and verify redirect to login and that /app is protected
    r2 = c.get('/logout', follow_redirects=True)
    print('/logout ->', r2.status_code)
    r3 = c.get('/app', follow_redirects=False)
    print('After logout, GET /app ->', r3.status_code, 'Location:', r3.headers.get('Location'))
