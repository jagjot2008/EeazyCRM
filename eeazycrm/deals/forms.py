from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Optional
from wtforms_sqlalchemy.fields import QuerySelectField

from eeazycrm.users.models import User
from eeazycrm.accounts.models import Account
from eeazycrm.contacts.models import Contact
from eeazycrm.deals.models import DealStage


class NewDeal(FlaskForm):
    title = StringField('Deal Title', validators=[DataRequired('Deal title is mandatory')])
    expected_close_price = FloatField('Expected Close Price',
                                      validators=[DataRequired('Expected Close Price is mandatory')])
    expected_close_date = DateTimeLocalField('Expected Close Date', format='%Y-%m-%dT%H:%M',
                                    validators=[Optional()])
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


def filter_deals_adv_filters_query():
    return [
        {'id': 1, 'title': 'All Expired Deals'},
        {'id': 2, 'title': 'All Active Deals'},
        {'id': 3, 'title': 'Deals Expiring Today'},
        {'id': 4, 'title': 'Deals Expiring In Next 7 Days'},
        {'id': 5, 'title': 'Deals Expiring In Next 30 Days'},
        {'id': 6, 'title': 'Created Today'},
        {'id': 7, 'title': 'Created Yesterday'},
        {'id': 8, 'title': 'Created In Last 7 Days'},
        {'id': 9, 'title': 'Created In Last 30 Days'}
    ]


def filter_deals_price_query():
    return [
        {'id': 1, 'title': '< 500'},
        {'id': 2, 'title': '>= 500 and < 1000'},
        {'id': 3, 'title': '>= 1000 and < 10,000'},
        {'id': 4, 'title': '>= 10,000 and < 50,000'},
        {'id': 5, 'title': '>= 50,000 and < 100,000'},
        {'id': 6, 'title': '>= 100,000'},
    ]


class FilterDeals(FlaskForm):
    txt_search = StringField()
    assignees = QuerySelectField(query_factory=User.user_list_query, get_pk=lambda a: a.id,
                                 get_label=User.get_label, allow_blank=True, blank_text='[-- Select Owner --]')

    accounts = QuerySelectField(query_factory=Account.account_list_query, get_pk=lambda a: a.id,
                                get_label=Account.get_label, blank_text='[-- Select Account --]', allow_blank=True)

    contacts = QuerySelectField(query_factory=Contact.contact_list_query, get_pk=lambda a: a.id,
                                get_label=Contact.get_label, blank_text='[-- Select Contact --]', allow_blank=True)

    deal_stages = QuerySelectField(query_factory=DealStage.deal_stage_list_query, get_pk=lambda a: a.id,
                                   get_label=DealStage.get_label, blank_text='[-- Deal Stage --]', allow_blank=True)

    price_range = QuerySelectField(query_factory=filter_deals_price_query,
                                   get_pk=lambda a: a['id'],
                                   get_label=lambda a: a['title'],
                                   allow_blank=True, blank_text='[-- Price Range --]')

    advanced_user = QuerySelectField(query_factory=filter_deals_adv_filters_query,
                                     get_pk=lambda a: a['id'],
                                     get_label=lambda a: a['title'],
                                     allow_blank=True, blank_text='[-- advanced filter --]')

    submit = SubmitField('Filter Deals')
