from datetime import datetime
from eeazycrm import db


class Contact(db.Model):
    id = db.Column(db.Integer, db.Sequence('contact_id_seq'), primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar = db.Column(db.String(25))
    phone = db.Column(db.String(20), nullable=False)
    mobile = db.Column(db.String(20))
    address_line = db.Column(db.String(40))
    addr_state = db.Column(db.String(20))
    addr_city = db.Column(db.String(20))
    post_code = db.Column(db.String(20))
    country = db.Column(db.String(20))
    notes = db.Column(db.String(200))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id', ondelete='cascade'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Account('{self.last_name}', '{self.email}', '{self.phone}')"
