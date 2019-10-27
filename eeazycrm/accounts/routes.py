from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request
from sqlalchemy import or_

from eeazycrm import db
from .models import Account

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

