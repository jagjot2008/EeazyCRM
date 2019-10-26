from configparser import ConfigParser

parser = ConfigParser()
parser.read('config.ini')


class Config:
    DEBUG = True
    SECRET_KEY = parser.get('session', 'SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = parser.get('database', 'DB_URI')
    RBAC_USE_WHITE = True





