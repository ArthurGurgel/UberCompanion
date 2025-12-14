from app import create_app

app = create_app()

with app.test_client() as c:
    # Prepare session as logged-in user
    with c.session_transaction() as sess:
        sess['user'] = 'tester'
        sess['user_id'] = 1

    r = c.get('/profile')
    html = r.data.decode()
    print('GET /profile ->', r.status_code)
    # Check presence of buttons and that password section is hidden by default
    print('Has show-password button:', 'id="show-password"' in html)
    print('Password section hidden by default:', 'id="password-section" class="hidden"' in html or 'id="password-section" class="hidden"' in html)
    # Ensure the profile form exists
    print('Has profile form:', 'id="profile-form"' in html)
