from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms_sqlalchemy.fields import QuerySelectField

from eeazycrm.settings.models import Currency, TimeZone, DEFAULT_ADDRESS


def date_format_query():
    return [
        {'key': '%d %B, %Y', 'val': '%d %B, %Y'},
    ]

def email_enc_query():
    return [
        {'key': 'none', 'val': 'NONE'},
        {'key': 'tls', 'val': 'TLS'},
    ]


class AppConfigForm(FlaskForm):
    default_currency = QuerySelectField('Default Currency', query_factory=Currency.get_list_query,
                                        get_pk=lambda a: a.id,
                                        get_label='name')
    default_timezone = QuerySelectField('Default TimeZone', query_factory=TimeZone.get_list_query,
                                        get_pk=lambda a: a.name,
                                        get_label='name')
    date_format = QuerySelectField('Date Format', query_factory=date_format_query,
                                    get_pk=lambda a: a['key'],
                                    get_label=lambda a: a['val'])

    address_format = TextAreaField('Default Address Format', default=DEFAULT_ADDRESS)

    smtp_server = StringField('SMTP Mail Server')
    smtp_port = StringField('SMTP Port')
    smtp_encryption = QuerySelectField('E-MAIL Encryption', query_factory=email_enc_query,
                                       get_pk=lambda a: a['key'], get_label=lambda a: a['val'])
    smtp_charset = StringField('SMTP Charset', default='utf-8')
    sender_name = StringField('Sender Name')
    sender_email = StringField('Sender Email')
    submit = SubmitField('Save')

