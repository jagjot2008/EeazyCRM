import pytest
from eeazycrm import create_app
from tests.actions.auth import AuthActions
from tests.actions.accounts import AccountActions


@pytest.fixture
def app():
    app = create_app()
    app.config['Testing'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def account(client):
    return AccountActions(client)

