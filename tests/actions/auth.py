class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='test@test.com', password='test'):
        return self._client.post(
            '/login',
            data=dict(email=email, password=password)
        )

    def new_user(self, last_name, email):
        return self._client.post(
            '/settings/staff/new',
            data=dict(last_name=last_name, email=email),
            follow_redirects=True
        )

    def remove_user(self, email):
        return self._client.delete(
            '/settings/staff/del/' + email,
            follow_redirects=True
        )

    def logout(self):
        return self._client.get('/logout')