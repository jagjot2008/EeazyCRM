from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email
from wtforms_sqlalchemy.fields import QuerySelectField

from eeazycrm.users.models import User


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
    assignees = QuerySelectField('Assign To', query_factory=User.user_list_query, get_pk=lambda a: a.id,
                                 get_label=User.get_label, default=User.get_current_user)
    submit = SubmitField('Create New Account')
