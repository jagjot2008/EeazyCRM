from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email
from wtforms_sqlalchemy.fields import QuerySelectField

from eeazycrm.leads.models import LeadSource
from eeazycrm.users.models import User


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