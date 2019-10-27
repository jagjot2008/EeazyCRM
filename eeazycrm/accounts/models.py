from datetime import datetime
from eeazycrm import db


class Account(db.Model):
    id = db.Column(db.Integer, db.Sequence('account_id_seq'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(100))
    email = db.Column(db.String(120), nullable=False)
    address_line = db.Column(db.String(40))
    addr_state = db.Column(db.String(20))
    addr_city = db.Column(db.String(20))
    post_code = db.Column(db.String(20))
    country = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    contacts = db.relationship(
        'Contact',
        uselist=False,
        backref='account',
        lazy=True
    )
    notes = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Account('{self.name}', '{self.email}', '{self.website}')"

