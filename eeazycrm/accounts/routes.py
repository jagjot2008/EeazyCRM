from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request
from sqlalchemy import or_

from eeazycrm import db
from .models import Account
from .forms import NewAccount

from eeazycrm.rbac import check_access

accounts = Blueprint('accounts', __name__)


@accounts.route("/accounts")
@login_required
@check_access('accounts', 'view')
def get_accounts_view():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('sq', None, type=str)
    search = f'%{search}%' if search else search

    accounts_list = Account.query\
        .filter(or_(
            Account.name.ilike(search),
            Account.website.ilike(search),
            Account.email.ilike(search),
            Account.address_line.ilike(search)
        ) if search else True)\
        .order_by(Account.date_created.desc())\
        .paginate(per_page=per_page, page=page)

    return render_template("accounts/accounts_list.html", title="Accounts View", accounts=accounts_list)


@accounts.route("/accounts/<int:account_id>")
@login_required
@check_access('accounts', 'view')
def get_account_view(account_id):
    account = Account.query.filter_by(id=account_id).first()
    return render_template("accounts/account_view.html", title="View Account", account=account)


@accounts.route("/accounts/new", methods=['GET', 'POST'])
@login_required
@check_access('accounts', 'create')
def new_account():
    form = NewAccount()
    if request.method == 'POST':
        if form.validate_on_submit():
            account = Account(name=form.name.data,
                              website=form.website.data,
                              email=form.email.data,
                              phone=form.phone.data,
                              address_line=form.address_line.data,
                              addr_state=form.addr_state.data,
                              addr_city=form.addr_city.data,
                              post_code=form.post_code.data,
                              country=form.country.data,
                              notes=form.notes.data)

            if current_user.role.name == 'admin':
                account.account_owner = form.assignees.data
            else:
                account.account_owner = current_user

            db.session.add(account)
            db.session.commit()
            flash('Account has been successfully created!', 'success')
            return redirect(url_for('accounts.get_accounts_view'))
        else:
            for error in form.errors:
                print(error)
            flash('Your form has errors! Please check the fields', 'danger')
    return render_template("accounts/new_account.html", title="New Account", form=form)

