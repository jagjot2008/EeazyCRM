from flask import render_template, flash, url_for, redirect, Blueprint, request
from eeazycrm import db, bcrypt
import os
import sys
from flask import current_app

from eeazycrm.install.forms import NewSystemUser
from eeazycrm.users.models import User
from eeazycrm.leads.models import Lead, LeadSource, LeadStatus
from eeazycrm.accounts.models import Account
from eeazycrm.contacts.models import Contact
from eeazycrm.deals.models import DealStage, Deal

install = Blueprint('install', __name__)


@install.route("/", methods=['GET', 'POST'])
@install.route("/install", methods=['GET', 'POST'])
def installation():
    step = request.args.get('step', default='sys_info', type=str)
    v = tuple(sys.version.split('.'))
    if v and int(v[0]) < 3 and int(v[1]) < 5:
        return render_template("install/error.html", title="Eeazy CRM installation failed",
                               reason=f"Python version >= {current_app.config['PYTHON_VER_MIN_REQUIRED']} is required for EeazyCRM")
    if step == 'create_sys_user':
        form = NewSystemUser()
        if request.method == 'POST':
            if form.validate_on_submit():

                # create all tables
                db.create_all()

                hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                user = User(first_name=form.first_name.data, last_name=form.last_name.data,
                             email=form.email.data, is_admin=True, is_first_login=False,
                             is_user_active=True, password=hashed_pwd)

                db.session.add(user)
                db.session.commit()
                return render_template("install/start.html", title="Welcome to EeazyCRM Installation",
                        form=form, step='company_info')
            else:
                return render_template("install/start.html", title="Welcome to EeazyCRM Installation",
                                       form=form, step='create_sys_user')
        elif request.method == 'GET':
            return render_template("install/start.html", title="Welcome to EeazyCRM Installation",
                                   form=form, step='create_sys_user')

    return render_template("install/start.html", title="Welcome to EeazyCRM Installation",
                           system_info=os.uname(), py_ver=sys.version, step='sys_info')


@current_app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('install.installation'))

