from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo


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

