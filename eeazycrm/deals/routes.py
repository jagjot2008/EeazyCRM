from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request
from sqlalchemy import or_

from eeazycrm import db
from .models import Deal, DealStage
from eeazycrm.accounts.models import Account
from .forms import NewDeal

from eeazycrm.rbac import check_access

deals = Blueprint('deals', __name__)


@deals.route("/deals")
@login_required
@check_access('deals', 'view')
def get_deals_view():
    view_t = request.args.get('view_t', 'list', type=str)
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

    if view_t == 'kanban':
        return render_template("deals/kanban_view.html", title="Deals View",
                               deals=deals_list,
                               deal_stages=DealStage.query.order_by(DealStage.display_order.asc()).all())
    else:
        return render_template("deals/deals_list.html", title="Deals View", deals=deals_list)


@deals.route("/deals/new", methods=['GET', 'POST'])
@login_required
@check_access('deals', 'create')
def new_deal():
    account = request.args.get('acc', None, type=int)
    form = NewDeal()

    if account:
        form.accounts.data = Account.get_account(account)

    if request.method == 'POST':
        if form.validate_on_submit():
            deal = Deal(title=form.title.data,
                        expected_close_price=form.expected_close_price.data,
                        expected_close_date=form.expected_close_date.data,
                        notes=form.notes.data)

            deal.account = form.accounts.data
            deal.contact = form.contacts.data
            deal.dealstage = form.deal_stages.data

            if current_user.role.name == 'admin':
                deal.deal_owner = form.assignees.data
            else:
                deal.deal_owner = current_user

            db.session.add(deal)
            db.session.commit()
            flash('Deal has been successfully created!', 'success')
            return redirect(url_for('deals.get_deals_view'))
        else:
            for error in form.errors:
                print(error)
            flash('Your form has errors! Please check the fields', 'danger')
    return render_template("deals/new_deal.html", title="New Deal", form=form)
