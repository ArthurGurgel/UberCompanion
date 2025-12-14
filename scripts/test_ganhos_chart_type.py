from app import create_app

app = create_app()

with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['user'] = 'tester'
        sess['user_id'] = 1

    # Read the JS file and verify ganhos chart uses 'bar' type
    js = open('static/js/app.js', 'r').read()
    has_bar = "type: 'bar'" in js and "Lucro Diário" in js
    print('JS has ganhos chart as bar:', has_bar)
    # Verify semanas_chart exists
    print('JS has semanas_chart var:', 'semanas_chart' in js)
