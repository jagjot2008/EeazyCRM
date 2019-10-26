from flask_login import current_user
import pytest


# test user login
def test_login(client, auth):
    assert client.get('/login').status_code == 200
    response = auth.login(email='admin@crm.com', password='123')
    assert response.headers['Location'] == 'http://localhost/home'

    with client:
        client.get('/')
        assert current_user.email == 'admin@crm.com'


# create a new staff member test
# inactive user should not be able to login
def test_new_user(client, auth):
    auth.login(email='admin@crm.com', password='123')
    assert client.get('/settings/staff/new').status_code == 200
    response = auth.new_user(last_name='Test', email='testuser@test.com')
    assert b'User has been successfully created!' in response.data

    auth.logout()

    response = auth.login(email='testuser@test.com', password='123')
    assert b"""User has not been granted access to the system!
                          Please contact the system administrator""" in response.data


# remove staff member by email
def test_remove_user(auth):
    auth.login(email='admin@crm.com', password='123')
    response = auth.remove_user('testuser@test.com')
    assert b'User removed successfully!' in response.data


@pytest.mark.parametrize(('email', 'password', 'message'), (
    ('admin20@thismail.com', '123', b'User does not exist! Please contact the system administrator'),
    ('admin@crm.com', '97972', b'Invalid Password!'),
))
def test_login_validate_input(auth, email, password, message):
    response = auth.login(email, password)
    assert message in response.data


# test new user form validation
@pytest.mark.parametrize(('last_name', 'email', 'message'), (
    (None, 'testmail@gmail.com', b'Please enter the last name'),
    ('White', None, b'Email address is mandatory'),
    ('White', 'jwhite@gmail', b'Please enter a valid email address e.g. abc@yourcompany.com'),
    ('Doe', 'admin@crm.com', b'Email already exists! Please choose a different one')
))
def test_new_user_validate_input(auth, last_name, email, message):
    auth.login(email='admin@crm.com', password='123')
    response = auth.new_user(last_name=last_name, email=email)
    assert message in response.data
