from flask import Blueprint, session
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request
from sqlalchemy import or_, text
from datetime import date, timedelta

from eeazycrm import db
from .models import Account
from eeazycrm.common.paginate import Paginate
from eeazycrm.common.filters import CommonFilters
from .forms import NewAccount, FilterAccounts, filter_accounts_adv_filters_query

from eeazycrm.rbac import check_access
from wtforms import Label

accounts = Blueprint('accounts', __name__)


def set_filters(f_id, module):
    today = date.today()
    filter_d = True
    if f_id == 1:
        filter_d = text("Account.is_active=True")
    elif f_id == 2:
        filter_d = text("Account.is_active=False")
    elif f_id == 3:
        filter_d = text("Date(%s.date_created)='%s'" % (module, today))
    elif f_id == 4:
        filter_d = text("Date(%s.date_created)='%s'" % (module, (today - timedelta(1))))
    elif f_id == 5:
        filter_d = text("Date(%s.date_created) > current_date - interval '7' day" % module)
    elif f_id == 6:
        filter_d = text("Date(%s.date_created) > current_date - interval '30' day" % module)
    return filter_d


def set_date_filters(filters, module, key):
    filter_d = True
    if request.method == 'POST':
        if filters.advanced_user.data:
            filter_d = set_filters(filters.advanced_user.data['id'], module)
            session[key] = filters.advanced_user.data['id']
    else:
        if key in session:
            filter_d = set_filters(session[key], module)
            filters.advanced_user.data = filter_accounts_adv_filters_query()[session[key] - 1]
    return filter_d


def reset_accounts_filters():
    if 'accounts_owner' in session:
        session.pop('accounts_owner', None)
    if 'accounts_search' in session:
        session.pop('accounts_search', None)
    if 'account_active' in session:
        session.pop('account_active', None)
    if 'accounts_date_created' in session:
        session.pop('accounts_date_created', None)


@accounts.route("/accounts", methods=['GET', 'POST'])
@login_required
@check_access('accounts', 'view')
def get_accounts_view():
    filters = FilterAccounts()
    search = CommonFilters.set_search(filters, 'accounts_search')
    owner = CommonFilters.set_owner(filters, 'Account', 'accounts_owner')
    advanced_filters = set_date_filters(filters, 'Account', 'accounts_date_created')

    query = Account.query.filter(or_(
        Account.name.ilike(f'%{search}%'),
        Account.website.ilike(f'%{search}%'),
        Account.email.ilike(f'%{search}%'),
        Account.phone.ilike(f'%{search}%'),
        Account.address_line.ilike(f'%{search}%'),
        Account.addr_state.ilike(f'%{search}%'),
        Account.addr_city.ilike(f'%{search}%'),
        Account.post_code.ilike(f'%{search}%')
    ) if search else True) \
        .filter(owner) \
        .filter(advanced_filters) \
        .order_by(Account.date_created.desc())

    return render_template("accounts/accounts_list.html", title="Accounts View",
                           accounts=Paginate(query=query), filters=filters)


@accounts.route("/accounts/edit/<int:account_id>", methods=['GET', 'POST'])
@login_required
@check_access('accounts', 'update')
def update_account(account_id):
    account = Account.get_account(account_id)
    if not account:
        return redirect(url_for('accounts.get_accounts_view'))

    form = NewAccount()
    if request.method == 'POST':
        if form.validate_on_submit():
            account.name = form.name.data
            account.website = form.website.data
            account.email = form.email.data
            account.phone = form.phone.data
            account.address_line = form.address_line.data
            account.addr_state = form.addr_state.data
            account.addr_city = form.addr_city.data
            account.post_code = form.post_code.data
            account.country = form.country.data
            account.account_owner = form.assignees.data
            account.notes = form.notes.data
            db.session.commit()
            flash('The account has been successfully updated', 'success')
            return redirect(url_for('accounts.get_account_view', account_id=account.id))
        else:
            print(form.errors)
            flash('Accounts update failed! Form has errors', 'danger')
    elif request.method == 'GET':
        form.name.data = account.name
        form.website.data = account.website
        form.email.data = account.email
        form.phone.data = account.phone
        form.address_line.data = account.address_line
        form.addr_state.data = account.addr_state
        form.addr_city.data = account.addr_city
        form.post_code.data = account.post_code
        form.country.data = account.country
        form.assignees.data = account.account_owner
        form.notes.data = account.notes
        form.submit.label = Label('update_account', 'Update Account')
    return render_template("accounts/new_account.html", title="Update Account", form=form)


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

            if current_user.is_admin:
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


@accounts.route("/accounts/del/<int:account_id>")
@login_required
@check_access('accounts', 'delete')
def delete_account(account_id):
    Account.query.filter_by(id=account_id).delete()
    db.session.commit()
    flash('Account removed successfully!', 'success')
    return redirect(url_for('accounts.get_accounts_view'))


@accounts.route("/accounts/reset_filters")
@login_required
@check_access('accounts', 'view')
def reset_filters():
    reset_accounts_filters()
    return redirect(url_for('accounts.get_accounts_view'))

