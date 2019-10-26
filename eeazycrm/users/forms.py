from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField

from .models import User, Role


class Register(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name',
                            validators=[DataRequired(message='Please enter the last name'), Length(min=2, max=20)])
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
    is_admin = BooleanField('Set Admin')
    submit = SubmitField('Sign Up!')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists! Please choose a different one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists! Please choose a different one')


class Login(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateProfile(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    picture = FileField('Update Avatar', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Update')


class ResourceForm(FlaskForm):
    resource_id = HiddenField('Resource ID')
    name = StringField('Resource Name',
                       validators=[DataRequired(message='Resource name is mandatory')])
    can_view = BooleanField('View')
    can_create = BooleanField('Create')
    can_edit = BooleanField('Update')
    can_delete = BooleanField('Delete')


class NewRoleForm(FlaskForm):
    name = StringField('Role Name',
                       validators=[DataRequired(message='Role name is mandatory')])
    permissions = FieldList(FormField(ResourceForm), min_entries=0)
    submit = SubmitField('Update Role')

    def validate_name(self, name):
        if name.data == 'admin':
            raise ValidationError(f'Role name \'{name.data}\' is reserved by the system! Please choose a different name')
        role = Role.get_by_name(name=name.data)
        if role:
            raise ValidationError(f'The role {role.name} already exists! Please choose a different name')


class UpdateRoleForm(FlaskForm):
    name = StringField('Role Name',
                       validators=[DataRequired(message='Role name is mandatory')])
    permissions = FieldList(FormField(ResourceForm), min_entries=0)
    submit = SubmitField('Update Role')


class UpdateUser(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name',
                            validators=[DataRequired(message='Please enter the last name'), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(
                            message='Email address is mandatory'),
                            Email(message='Please enter a valid email address e.g. abc@yourcompany.com')])
    password = PasswordField('Password')
    picture = FileField('Update Avatar',
                        validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    role = QuerySelectField(query_factory=lambda: Role.query, get_pk=lambda a: a.id,
                            get_label='name', allow_blank=False,
                            validators=[DataRequired(message='Role assignment is mandatory')])
    is_admin = BooleanField('Set Admin')
    is_user_active = BooleanField('Set Active')
    is_first_login = BooleanField('User Should Change Password on Login')
    permissions = FieldList(FormField(ResourceForm), min_entries=0)
    submit = SubmitField('Update Staff Member')

    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user:
    #         raise ValidationError(f'Email {email.data} already exists! Please choose a different one')
