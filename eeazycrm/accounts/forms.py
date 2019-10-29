from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, SubmitField, HiddenField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email
from wtforms_sqlalchemy.fields import QuerySelectField

from .models import Account
from eeazycrm.users.models import User


def user_list_query():
    return User.query


def get_user():
    return User.query.filter_by(id=current_user.id).first()


def get_label(user):
    return user.get_name()


class NewAccount(FlaskForm):
    name = StringField('Account Name', validators=[DataRequired(message='Account name is mandatory')])
    website = StringField('Website')
    email = StringField('Email',
                        validators=[DataRequired(message='Email address is mandatory'),
                                    Email(message='Please enter a valid email address e.g. abc@yourcompany.com')])
    phone = StringField('Phone')
    address_line = StringField('Address')
    addr_state = StringField('State')
    addr_city = StringField('City')
    post_code = StringField('Postcode')
    country = StringField('Country')
    notes = StringField('Notes', widget=TextArea())
    assignees = QuerySelectField('Assign To', query_factory=user_list_query, get_pk=lambda a: a.id,
                                 get_label=get_label, default=get_user)
    submit = SubmitField('Create New Account')
