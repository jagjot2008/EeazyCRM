from flask_login import current_user
import pytest


# test new account form validation
@pytest.mark.parametrize(('name', 'email', 'message'), (
    (None, 'testemail@gamil.com', b'Account name is mandatory'),
    ('ABS India P. Ltd.', None, b'Email address is mandatory'),
    ('ABS India P. Ltd.', 'jwhite@gmail', b'Please enter a valid email address e.g. abc@yourcompany.com')
))
def test_new_account_validate_input(auth, account, name, email, message):
    auth.login(email='admin@crm.com', password='123')
    acc_param = dict(name=name, email=email)
    response = account.new_account(acc_param)
    assert message in response.data


# test create a new account
def test_new_account(client, auth, account):
    auth.login(email='admin@crm.com', password='123')
    assert client.get('/accounts/new').status_code == 200

    acc_params = dict(name='Anton Villsen Co.', email='testmail@gmail.com')
    response = account.new_account(acc_params)
    assert b'Account has been successfully created!' in response.data
