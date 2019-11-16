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


@accounts.route("/accounts", methods=['GET', 'POST'])
@login_required
@check_access('accounts', 'view')
def get_accounts_view():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = None
    filters = FilterAccounts()

    if request.method == 'POST':
        today = date.today()
        date_today_filter = True
        active = True
        if current_user.role.name == 'admin':
            if filters.assignees.data:
                owner = text('Account.owner_id=%d' % filters.assignees.data.id)
                session['accounts_owner'] = filters.assignees.data.id
            else:
                owner = True
        else:
            owner = text('Account.owner_id=%d' % current_user.id)
            session['accounts_owner'] = current_user.id

        if filters.advanced_user.data:
            if filters.advanced_user.data['title'] == 'Active':
                active = text("Account.is_active=True")
            elif filters.advanced_user.data['title'] == 'Inactive':
                active = text("Account.is_active=False")
            elif filters.advanced_user.data['title'] == 'Created Today':
                date_today_filter = text("Date(Account.date_created)='%s'" % today)
            elif filters.advanced_user.data['title'] == 'Created Yesterday':
                date_today_filter = text("Date(Account.date_created)='%s'" % (today - timedelta(1)))
            elif filters.advanced_user.data['title'] == 'Created In Last 7 Days':
                date_today_filter = text("Date(Account.date_created) > current_date - interval '7' day")
            elif filters.advanced_user.data['title'] == 'Created In Last 30 Days':
                date_today_filter = text("Date(Account.date_created) > current_date - interval '30' day")

        search = filters.txt_search.data
        if search:
            session['accounts_search'] = search

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
            .filter(date_today_filter) \
            .order_by(Account.date_created.desc()) \
            .paginate(per_page=per_page, page=page)
    else:
        if 'accounts_owner' in session:
            owner = text('Account.owner_id=%d' % session['accounts_owner'])
        else:
            owner = True if current_user.role.name == 'admin' else text('Account.owner_id=%d' % current_user.id)

        if 'accounts_search' in session:
            search = session['accounts_search']

        query = Account.query \
            .filter(or_(
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
            .order_by(Account.date_created.desc()) \
            .paginate(per_page=per_page, page=page)

    if 'accounts_owner' in session:
        filters.assignees.data = User.get_by_id(session['accounts_owner'])

    if 'accounts_search' in session:
        filters.txt_search.data = session['accounts_search']

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
    if 'accounts_owner' in session:
        del session['accounts_owner']
    if 'accounts_search' in session:
        del session['accounts_search']
    return redirect(url_for('accounts.get_accounts_view'))

