from eeazycrm import db, login_manager
from flask_login import UserMixin, current_user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
    first_name = db.Column(db.String(20), nullable=True)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar = db.Column(db.String(25), nullable=True)
    password = db.Column(db.String(60), nullable=False)
    leads = db.relationship('Lead', backref='owner', lazy=True)
    accounts = db.relationship('Account', backref='account_owner', lazy=True)
    contacts = db.relationship('Contact', backref='contact_owner', lazy=True)
    deals = db.relationship('Deal', backref='deal_owner', lazy=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_first_login = db.Column(db.Boolean, nullable=False, default=True)
    is_user_active = db.Column(db.Boolean, nullable=False, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='SET NULL'), nullable=True)

    @staticmethod
    def get_label(user):
        return user.get_name()

    @staticmethod
    def user_list_query():
        return User.query

    @staticmethod
    def get_current_user():
        return User.query.filter_by(id=current_user.id).first()

    @staticmethod
    def get_by_id(user_id):
        return User.query.filter_by(id=user_id).first()

    def get_name(self):
        return self.first_name + ' ' + self.last_name

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.email}', '{self.avatar}')"


roles_resources = db.Table(
    'roles_resources',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('resource_id', db.Integer, db.ForeignKey('resource.id'))
)


class Role(db.Model):
    id = db.Column(db.Integer, db.Sequence('role_id_seq'), primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    user = db.relationship(
        'User',
        uselist=False,
        backref='role',
        lazy=True
    )
    resources = db.relationship(
        'Resource',
        secondary=roles_resources,
        backref=db.backref('resources', lazy='dynamic')
    )

    @staticmethod
    def get_by_name(name):
        return Role.query.filter_by(name=name).first()

    @staticmethod
    def get_by_id(role_id):
        return Role.query.filter_by(id=role_id).first()

    def set_permissions(self, resources):
        for ind in range(len(resources)):
            self.resources[ind].can_view = resources[ind].can_view.data
            self.resources[ind].can_create = resources[ind].can_create.data
            self.resources[ind].can_edit = resources[ind].can_edit.data
            self.resources[ind].can_delete = resources[ind].can_delete.data


class Resource(db.Model):
    id = db.Column(db.Integer, db.Sequence('resource_id_seq'), primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    can_view = db.Column(db.Boolean, nullable=False)
    can_edit = db.Column(db.Boolean, nullable=False)
    can_create = db.Column(db.Boolean, nullable=False)
    can_delete = db.Column(db.Boolean, nullable=False)
