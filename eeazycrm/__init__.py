from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

import os

from .config import DevelopmentConfig, TestConfig, ProductionConfig

# database handle
db = SQLAlchemy(session_options={"autoflush": False})

# encryptor handle
bcrypt = Bcrypt()

# manage user login
login_manager = LoginManager()

# function name of the login route that
# tells the path which facilitates authentication
login_manager.login_view = 'users.login'


def run_install(app_ctx):
    from eeazycrm.install.routes import install
    app_ctx.register_blueprint(install)
    return app_ctx


def create_app(config_class=ProductionConfig):
    app = Flask(__name__, instance_relative_config=True)

    if os.getenv('FLASK_ENV') == 'development':
        config_class = DevelopmentConfig()
    elif os.getenv('FLASK_ENV') == 'production':
        config_class = ProductionConfig()
    elif os.getenv('FLASK_ENV') == 'testing':
        config_class = TestConfig()

    app.config.from_object(config_class)
    app.url_map.strict_slashes = False
    app.jinja_env.globals.update(zip=zip)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # check if the config table exists, otherwise run install
        engine = db.get_engine(app)
        if not engine.dialect.has_table(engine, 'app_config'):
            return run_install(app)
        else:
            from eeazycrm.settings.models import AppConfig
            row = AppConfig.query.first()
            if not row:
                return run_install(app)

        # application is installed so extends the config
        from eeazycrm.settings.models import AppConfig, Currency, TimeZone
        app_cfg = AppConfig.query.first()
        app.config['def_currency'] = Currency.get_currency_by_id(app_cfg.default_currency)
        app.config['def_tz'] = TimeZone.get_tz_by_id(app_cfg.default_timezone)

        # include the routes
        # from eeazycrm import routes
        from eeazycrm.main.routes import main
        from eeazycrm.users.routes import users
        from eeazycrm.leads.routes import leads
        from eeazycrm.accounts.routes import accounts
        from eeazycrm.contacts.routes import contacts
        from eeazycrm.deals.routes import deals
        from eeazycrm.settings.routes import settings
        from eeazycrm.settings.app_routes import app_config
        from eeazycrm.reports.routes import reports

        # register routes with blueprint
        app.register_blueprint(main)
        app.register_blueprint(users)
        app.register_blueprint(settings)
        app.register_blueprint(app_config)
        app.register_blueprint(leads)
        app.register_blueprint(accounts)
        app.register_blueprint(contacts)
        app.register_blueprint(deals)
        app.register_blueprint(reports)
        return app


