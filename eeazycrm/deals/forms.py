from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.fields.html5 import DateField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField

from eeazycrm.users.models import User
from eeazycrm.accounts.models import Account
from eeazycrm.contacts.models import Contact
from eeazycrm.deals.models import DealStage


class NewDeal(FlaskForm):
    title = StringField('Deal Title', validators=[DataRequired('Deal title is mandatory')])
    expected_close_price = FloatField('Expected Close Price',
                                      validators=[DataRequired('Expected Close Price is mandatory')])
    expected_close_date = DateField('Expected Close Date', format='%Y-%m-%d')
    deal_stages = QuerySelectField('Deal Stage', query_factory=DealStage.deal_stage_list_query, get_pk=lambda a: a.id,
                                 get_label=DealStage.get_label, allow_blank=False,
                                 validators=[DataRequired(message='Please select deal stage')])
    accounts = QuerySelectField('Account', query_factory=Account.account_list_query, get_pk=lambda a: a.id,
                                 get_label=Account.get_label, blank_text='Select An Account', allow_blank=True,
                                validators=[DataRequired(message='Please choose an account for the deal')])
    contacts = QuerySelectField('Contact', query_factory=Contact.contact_list_query, get_pk=lambda a: a.id,
                                 get_label=Contact.get_label, blank_text='Select A Contact', allow_blank=True)
    assignees = QuerySelectField('Assign To', query_factory=User.user_list_query, get_pk=lambda a: a.id,
                                 get_label=User.get_label, default=User.get_current_user)
    notes = StringField('Notes', widget=TextArea())
    submit = SubmitField('Create New Deal')
