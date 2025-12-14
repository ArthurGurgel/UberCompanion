from app import create_app

app = create_app()

with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['user'] = 'tester'
        sess['user_id'] = 1

    r = c.get('/app')
    html = r.data.decode()
    print('GET /app ->', r.status_code)
    print('Has nav separator:', 'class="nav-separator"' in html)
    # ensure separator sits between relatorios and logout anchor
    rel_idx = html.find('📈 Relatórios')
    sep_idx = html.find('class="nav-separator"')
    logout_idx = html.find('🔒 Sair')
    print('Order relatorios < separator < logout:', rel_idx < sep_idx < logout_idx)
