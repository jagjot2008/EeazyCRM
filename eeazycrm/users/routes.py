from flask import Blueprint, session
from flask_login import current_user, login_user, logout_user
from flask import render_template, flash, url_for, redirect, request

from eeazycrm import db, bcrypt
from .forms import Register, Login
from .models import User

users = Blueprint('users', __name__)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = Login()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if not user.is_user_active:
                    flash("""User has not been granted access to the system!
                          Please contact the system administrator""",
                          'danger')
                elif not bcrypt.check_password_hash(user.password, form.password.data):
                    flash('Invalid Password!', 'danger')
                else:
                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('User does not exist! Please contact the system administrator', 'danger')
    return render_template("login.html", title="EeazyCRM - Login", form=form)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = Register()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(first_name=form.first_name.data, last_name=form.last_name.data,
                        email=form.email.data, is_admin=True, is_first_login=False,
                        is_user_active=True, password=hashed_pwd)
            db.session.add(user)
            db.session.commit()
            flash('User has been created! You can now login', 'success')
            return redirect(url_for('users.login'))
        else:
            flash(f'Failed to register user!', 'danger')
    return render_template("register.html", title="EeazyCRM - Register New User", form=form)


@users.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('users.login'))


