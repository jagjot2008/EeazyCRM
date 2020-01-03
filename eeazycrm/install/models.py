from eeazycrm import db


class User(db.Model):
    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
    first_name = db.Column(db.String(20), nullable=True)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar = db.Column(db.String(25), nullable=True)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_first_login = db.Column(db.Boolean, nullable=False, default=True)
    is_user_active = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.email}')"