from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request
from sqlalchemy import or_

from eeazycrm import db
from .models import Deal

from eeazycrm.rbac import check_access

deals = Blueprint('deals', __name__)


@deals.route("/deals")
@login_required
@check_access('deals', 'view')
def get_deals_view():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('sq', None, type=str)
    search = f'%{search}%' if search else search

    deals_list = Deal.query\
        .filter(or_(
            Deal.name.ilike(search),
            Deal.website.ilike(search),
            Deal.email.ilike(search),
            Deal.address_line.ilike(search)
        ) if search else True)\
        .order_by(Deal.date_created.desc())\
        .paginate(per_page=per_page, page=page)

    return render_template("deals/deals_list.html", title="Deals View", deals=deals_list)
