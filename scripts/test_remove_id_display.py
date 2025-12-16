from app import create_app

app = create_app()

with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['user'] = 'tester'
        sess['user_id'] = 1

    for path in ['/', '/app']:
        r = c.get(path)
        html = r.data.decode()
        print(path, 'status', r.status_code)
        print('Has ID header?', '<th>ID' in html)
        # Check colspan values
        print('Has ganhos empty colspan 6?', 'colspan="6"' in html)
        print('Has abastecimentos empty colspan 5?', 'colspan="5"' in html)
        print('---')
