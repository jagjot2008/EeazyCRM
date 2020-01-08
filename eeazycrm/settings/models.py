from datetime import datetime
from eeazycrm import db
from flask_login import current_user

DEFAULT_ADDRESS = '{address_line}\n{address_state}, {address_city}-{post_code}\n{address_country}'


class Currency(db.Model):
    id = db.Column(db.Integer, db.Sequence('currency_id_seq'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    iso_code = db.Column(db.String(10), nullable=False)
    symbol = db.Column(db.String(10), nullable=True)

    @staticmethod
    def get_list_query():
        return Currency.query

    @staticmethod
    def get_currency_by_id(currency_id):
        return Currency.query.filter_by(id=currency_id).first()

    def __repr__(self):
        return f"Currency('{self.name}', '{self.iso_code}')"


class TimeZone(db.Model):
    id = db.Column(db.Integer, db.Sequence('timezone_id_seq'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    @staticmethod
    def get_list_query():
        return TimeZone.query

    @staticmethod
    def get_tz_by_id(tz_id):
        return TimeZone.query.filter_by(id=tz_id).first()

    @staticmethod
    def get_tz_by_name(tz_name):
        return TimeZone.query.filter_by(name=tz_name).first()

    def __repr__(self):
        return f"TimeZone('{self.name}')"


class AppConfig(db.Model):
    id = db.Column(db.Integer, db.Sequence('app_config_id_seq'), primary_key=True)
    default_currency = db.Column(db.Integer, db.ForeignKey('currency.id', ondelete='SET NULL'), nullable=False)
    default_timezone = db.Column(db.Integer, db.ForeignKey('time_zone.id', ondelete='SET NULL'), nullable=False)
    date_format = db.Column(db.String(20), nullable=True, default='%Y-%m-d%')
    address_format = db.Column(db.String(200), nullable=True,
                               default=DEFAULT_ADDRESS)
    smtp_server = db.Column(db.String(50), nullable=True)
    smtp_encryption = db.Column(db.String(5), nullable=True)
    smtp_port = db.Column(db.String(5), nullable=True)
    smtp_charset = db.Column(db.String(5), nullable=True, default='utf-8')
    sender_name = db.Column(db.String(50), nullable=True)
    sender_email = db.Column(db.String(100), nullable=True)

    currency = db.relationship(
        'Currency',
        backref='app_config',
        uselist=False,
        lazy=True
    )

    time_zone = db.relationship(
        'TimeZone',
        backref='app_config',
        uselist=False,
        lazy=True
    )
