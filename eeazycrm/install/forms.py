from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField

from eeazycrm.settings.models import Currency, TimeZone


class NewSystemUser(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message='Please enter your first name')])
    last_name = StringField('Last Name',
                            validators=[DataRequired(message='Please enter your last name'), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(
                            message='Email address is mandatory'),
                            Email(message='Please enter a valid email address e.g. abc@yourcompany.com')])
    password = PasswordField('Password',
                             validators=[DataRequired(message='Password is mandatory')])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(
                                         message='Confirm Password is mandatory'),
                                         EqualTo('password', 'Passwords do not match')])
    submit = SubmitField('Next: Setup Company Details')


class CurrencyTz(FlaskForm):
    currency = QuerySelectField('Default Currency', query_factory=Currency.get_list_query, get_pk=lambda a: a.id,
                                get_label='name',
                                validators=[DataRequired(message='Please select default currency')])
    time_zone = QuerySelectField('Your Time Zone', query_factory=TimeZone.get_list_query, get_pk=lambda a: a.id,
                                 get_label='name',
                                 validators=[DataRequired(message='Please select your timezone')])
    submit = SubmitField('Next: Finish Installation')


class FinishInstall(FlaskForm):
    import_sample_data = BooleanField('Install Sample Data')
    submit = SubmitField('Complete Installation')

