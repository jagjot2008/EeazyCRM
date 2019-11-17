from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email
from wtforms_sqlalchemy.fields import QuerySelectField

from eeazycrm.users.models import User
from eeazycrm.accounts.models import Account


class NewContact(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('First Name', validators=[DataRequired(message='Last name is mandatory')])
    email = StringField('Email',
                        validators=[DataRequired(message='Email address is mandatory'),
                                    Email(message='Please enter a valid email address e.g. abc@yourcompany.com')])
    phone = StringField('Phone')
    mobile = StringField('Mobile')
    avatar = FileField('Contact Avatar', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    address_line = StringField('Address')
    addr_state = StringField('State')
    addr_city = StringField('City')
    post_code = StringField('Postcode')
    country = StringField('Country')
    notes = StringField('Notes', widget=TextArea())
    accounts = QuerySelectField('Account', query_factory=Account.account_list_query, get_pk=lambda a: a.id,
                                 get_label=Account.get_label, blank_text='Select An Account', allow_blank=True,
                                validators=[DataRequired(message='Please choose an account for the contact')])
    assignees = QuerySelectField('Assign To', query_factory=User.user_list_query, get_pk=lambda a: a.id,
                                 get_label=User.get_label, default=User.get_current_user)
    submit = SubmitField('Create New Contact')


def filter_contacts_adv_filters_query():
    return [
        {'id': 1, 'title': 'Created Today'},
        {'id': 2, 'title': 'Created Yesterday'},
        {'id': 3, 'title': 'Created In Last 7 Days'},
        {'id': 4, 'title': 'Created In Last 30 Days'}
    ]


class FilterContacts(FlaskForm):
    txt_search = StringField()
    accounts = QuerySelectField(query_factory=Account.account_list_query, get_pk=lambda a: a.id,
                                get_label=Account.get_label, blank_text='[-- Select Account--]', allow_blank=True)
    assignees = QuerySelectField(query_factory=User.user_list_query, get_pk=lambda a: a.id,
                                 get_label=User.get_label, allow_blank=True, blank_text='[-- Select Owner --]')
    advanced_user = QuerySelectField(query_factory=filter_contacts_adv_filters_query,
                                     get_pk=lambda a: a['id'],
                                     get_label=lambda a: a['title'],
                                     allow_blank=True, blank_text='[-- advanced filter --]')

    submit = SubmitField('Filter Contacts')
