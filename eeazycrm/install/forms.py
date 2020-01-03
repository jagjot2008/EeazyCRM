from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class SetupDatabaseForm(FlaskForm):
    db_host = StringField('Host', validators=[DataRequired(message='Database host is mandatory')], default='localhost')
    db_user = StringField('Username', validators=[DataRequired(message='Database username is mandatory')])
    db_pass = PasswordField('Password')
    db_name = StringField('Database Name', validators=[DataRequired(message='Database name is mandatory')])
    submit = SubmitField('Next: Create Root User')

