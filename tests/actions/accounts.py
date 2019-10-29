class AccountActions(object):
    def __init__(self, client):
        self._client = client

    def new_account(self, acc_params):
        return self._client.post(
            '/accounts/new',
            data=acc_params,
            follow_redirects=True
        )