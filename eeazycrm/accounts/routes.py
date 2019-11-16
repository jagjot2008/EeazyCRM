from flask import Blueprint, session
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request
from sqlalchemy import or_, text
from datetime import date, timedelta

from eeazycrm import db
from .models import Account
from eeazycrm.users.models import User
from .forms import NewAccount, FilterAccounts

from eeazycrm.rbac import check_access

accounts = Blueprint('accounts', __name__)


def set_owner(filters, module, key):
    if not module or not filters or not key:
        return None

    if request.method == 'POST':
        if current_user.role.name == 'admin':
            if filters.assignees.data:
                owner = text('%s.owner_id=%d' % (module, filters.assignees.data.id))
                session[key] = filters.assignees.data.id
            else:
                owner = True
        else:
            owner = text('%s.owner_id=%d' % (module, current_user.id))
            session[key] = current_user.id
    else:
        if key in session:
            owner = text('%s.owner_id=%d' % (module, session[key]))
            filters.assignees.data = User.get_by_id(session[key])
        else:
            owner = True if current_user.role.name == 'admin' else text('%s.owner_id=%d' % (module, current_user.id))
    return owner


def set_search(filters, key):
    search = None
    if request.method == 'POST':
        search = filters.txt_search.data
        session[key] = search

    if key in session:
        filters.txt_search.data = session[key]
        search = session[key]
    return search


def set_date_filters(filters, module, key):
    today = date.today()
    date_created_filter = True
    if request.method == 'POST':
        if filters.advanced_user.data:
            session[key] = filters.advanced_user.data['id']
            if filters.advanced_user.data['title'] == 'Created Today':
                date_created_filter = text("Date(%s.date_created)='%s'" % (module, today))
            elif filters.advanced_user.data['title'] == 'Created Yesterday':
                date_created_filter = text("Date(%s.date_created)='%s'" % (module, (today - timedelta(1))))
            elif filters.advanced_user.data['title'] == 'Created In Last 7 Days':
                date_created_filter = text("Date(%s.date_created) > current_date - interval '7' day" % module)
            elif filters.advanced_user.data['title'] == 'Created In Last 30 Days':
                date_created_filter = text("Date(%s.date_created) > current_date - interval '30' day" % module)

    if key in session:
        filters.advanced_user.data['id'] = session[key]
    return date_created_filter


def reset_accounts_filters():
    if 'accounts_owner' in session:
        del session['accounts_owner']
    if 'accounts_search' in session:
        del session['accounts_search']
    if 'account_active' in session:
        del session['account_active']
    if 'accounts_date_created' in session:
        del session['accounts_date_created']


def set_active_filter(filters, key):
    active = True
    if request.method == 'POST':
        if filters.advanced_user.data:
            if filters.advanced_user.data['title'] == 'Active':
                active = text("Account.is_active=True")
                session[key] = filters.advanced_user.data['id']
            elif filters.advanced_user.data['title'] == 'Inactive':
                active = text("Account.is_active=False")
                session[key] = filters.advanced_user.data['id']

    if key in session:
        filters.advanced_user.data['id'] = session[key]
    return active


@accounts.route("/accounts", methods=['GET', 'POST'])
@login_required
@check_access('accounts', 'view')
def get_accounts_view():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    filters = FilterAccounts()

    search = set_search(filters, 'accounts_search')
    owner = set_owner(filters, 'Account', 'accounts_owner')
    active = set_active_filter(filters, 'account_active')
    date_created_filter = set_date_filters(filters, 'Account', 'accounts_date_created')

    print(search)

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
        .filter(active) \
        .filter(date_created_filter) \
        .order_by(Account.date_created.desc()) \
        .paginate(per_page=per_page, page=page)

    return render_template("accounts/accounts_list.html", title="Accounts View",
                           accounts=query, filters=filters)


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

