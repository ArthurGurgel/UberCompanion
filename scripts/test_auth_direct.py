from app.models import User

# replace with one of the emails found by inspect_users.py
print('Autenticar test122291@example.com / senha123 ->', User.autenticar('test122291@example.com', 'senha123'))
print('Autenticar testuser14440 / senha123 ->', User.autenticar('testuser14440', 'senha123'))
