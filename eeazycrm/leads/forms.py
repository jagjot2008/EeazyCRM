from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields.html5 import DateField
from wtforms import StringField, SubmitField, FloatField, BooleanField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email, Optional
from wtforms_sqlalchemy.fields import QuerySelectField

from eeazycrm.leads.models import LeadSource
from eeazycrm.users.models import User
from eeazycrm.accounts.models import Account
from eeazycrm.contacts.models import Contact
from eeazycrm.deals.models import DealStage


def lead_source_query():
    return LeadSource.query


class NewLead(FlaskForm):
    title = StringField('Lead Title')
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    email = StringField('Email', validators=[DataRequired(), Email()])
    company = StringField('Company Name')
    address_line = StringField('Address')
    addr_state = StringField('State')
    addr_city = StringField('City')
    post_code = StringField('Postcode')
    country = StringField('Country')
    notes = StringField('Notes', widget=TextArea())
    lead_source = QuerySelectField(query_factory=lead_source_query, get_pk=lambda a: a.id,
                                   get_label='source_name', allow_blank=True, blank_text='Select Lead Source')

    assignees = QuerySelectField('Assign To', query_factory=User.user_list_query, get_pk=lambda a: a.id,
                                 get_label=User.get_label, default=User.get_current_user)
    submit = SubmitField('Create New Lead')


class ImportLeads(FlaskForm):
    csv_file = FileField('CSV File', validators=[FileAllowed(['csv'])])
    lead_source = QuerySelectField(query_factory=lead_source_query, get_pk=lambda a: a.id,
                                   get_label='source_name', allow_blank=True, blank_text='Set Lead Source')
    submit = SubmitField('Create Leads')


class ConvertLead(FlaskForm):
    title = StringField('Deal Title', validators=[DataRequired('Deal title is mandatory')])
    use_account_information = BooleanField('Use Account Information', default=True)
    account_name = StringField('Account Name')
    account_email = StringField('Account Email')
    accounts = QuerySelectField('Account', query_factory=Account.account_list_query, get_pk=lambda a: a.id,
                                get_label=Account.get_label, blank_text='Select An Account', allow_blank=True)

    use_contact_information = BooleanField('Use Contact Information', default=False)
    contact_first_name = StringField('Contact First Name')
    contact_last_name = StringField('Contact Last Name')
    contact_email = StringField('Contact Email',
                                validators=[Optional(), Email(message='Invalid email address!')])
    contact_phone = StringField('Contact Phone')
    contacts = QuerySelectField('Contact', query_factory=Contact.contact_list_query, get_pk=lambda a: a.id,
                                get_label=Contact.get_label, blank_text='Select A Contact', allow_blank=True)

    create_deal = BooleanField('Create Deal', default=True)

    expected_close_price = FloatField('Expected Close Price',
                                      validators=[DataRequired('Expected Close Price is mandatory')])
    expected_close_date = DateField('Expected Close Date', format='%Y-%m-%d',
                                    validators=[Optional()])
    deal_stages = QuerySelectField('Deal Stage', query_factory=DealStage.deal_stage_list_query, get_pk=lambda a: a.id,
                                   get_label=DealStage.get_label, allow_blank=False,
                                   validators=[DataRequired(message='Please select deal stage')])

    assignees = QuerySelectField('Assign To', query_factory=User.user_list_query, get_pk=lambda a: a.id,
                                 get_label=User.get_label, default=User.get_current_user)
    submit = SubmitField('Covert Lead')


