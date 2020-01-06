from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from eeazycrm.config import DevelopmentConfig, TestConfig, ProductionConfig

import os

app = Flask(__name__, instance_relative_config=True)

config_class = ProductionConfig()
if os.getenv('FLASK_ENV') == 'development':
    config_class = DevelopmentConfig()
elif os.getenv('FLASK_ENV') == 'production':
    config_class = ProductionConfig()
elif os.getenv('FLASK_ENV') == 'testing':
    config_class = TestConfig()

app.config.from_object(config_class)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


class TestUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))


if __name__ == '__main__':
    manager.run()
