from datetime import datetime
from eeazycrm import db
from flask_login import current_user


class Account(db.Model):
    id = db.Column(db.Integer, db.Sequence('account_id_seq'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(100))
    email = db.Column(db.String(120), nullable=False)
    address_line = db.Column(db.String(40))
    addr_state = db.Column(db.String(40))
    addr_city = db.Column(db.String(40))
    post_code = db.Column(db.String(20))
    country = db.Column(db.String(40))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    contacts = db.relationship(
        'Contact',
        cascade='all,delete',
        backref='account',
        passive_deletes=True,
        lazy=True
    )
    deals = db.relationship(
        'Deal',
        cascade='all,delete',
        backref='account',
        passive_deletes=True,
        lazy=True
    )
    notes = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @staticmethod
    def account_list_query():
        if current_user.is_admin:
            return Account.query
        else:
            return Account.query.filter_by(owner_id=current_user.id)

    @staticmethod
    def get_label(account):
        return account.name

    @staticmethod
    def get_account(account_id):
        return Account.query.filter_by(id=account_id).first()

    def __repr__(self):
        return f"Account('{self.name}', '{self.email}', '{self.website}')"

