from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request
from sqlalchemy import or_, text
from datetime import date, timedelta
import json

from eeazycrm import db
from .models import Deal, DealStage
from eeazycrm.accounts.models import Account
from .forms import NewDeal, FilterDeals

from eeazycrm.rbac import check_access

deals = Blueprint('deals', __name__)


@deals.route("/deals", methods=['GET', 'POST'])
@login_required
@check_access('deals', 'view')
def get_deals_view():
    view_t = request.args.get('view_t', 'list', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    filters = FilterDeals()

    if request.method == 'POST':
        today = date.today()
        date_today_filter = True
        price = True

        if current_user.role.name == 'admin':
            owner = text('Deal.owner_id=%d' % filters.assignees.data.id) if filters.assignees.data else True
        else:
            owner = text('Deal.owner_id=%d' % current_user.id)

        account = text('Deal.account_id=%d' % filters.accounts.data.id) if filters.accounts.data else True
        contact = text('Deal.contact_id=%d' % filters.contacts.data.id) if filters.contacts.data else True

        if filters.advanced_user.data:
            if filters.advanced_user.data['title'] == 'All Expired Deals':
                date_today_filter = text("current_timestamp > Deal.expected_close_date")
            elif filters.advanced_user.data['title'] == 'All Active Deals':
                date_today_filter = text("current_timestamp <= Deal.expected_close_date OR "
                                         "Date(Deal.expected_close_date) IS NULL")
            elif filters.advanced_user.data['title'] == 'Deals Expiring Today':
                date_today_filter = text("expected_close_date "
                                         "BETWEEN date_trunc('day', current_timestamp) AND "
                                         "date_trunc('day', current_timestamp) + interval '1 day' - interval '1 second'")
            elif filters.advanced_user.data['title'] == 'Deals Expiring In Next 7 Days':
                date_today_filter = text("expected_close_date "
                                         "BETWEEN date_trunc('day', current_timestamp) + interval '1 day' AND "
                                         "date_trunc('day', current_timestamp) + interval '7 day' - interval '1 second'")
            elif filters.advanced_user.data['title'] == 'Deals Expiring In Next 30 Days':
                date_today_filter = text("expected_close_date "
                                         "BETWEEN date_trunc('day', current_timestamp) + interval '1 day' AND "
                                         "date_trunc('day', current_timestamp)"
                                         " + interval '30 day' - interval '1 second'")
            elif filters.advanced_user.data['title'] == 'Created Today':
                date_today_filter = text("date(Deal.date_created)='%s'" % today)
            elif filters.advanced_user.data['title'] == 'Created Yesterday':
                date_today_filter = text("date(Deal.date_created)='%s'" % (today - timedelta(1)))
            elif filters.advanced_user.data['title'] == 'Created In Last 7 Days':
                date_today_filter = text("date(Deal.date_created) > current_date - interval '7' day")
            elif filters.advanced_user.data['title'] == 'Created In Last 30 Days':
                date_today_filter = text("date(Deal.date_created) > current_date - interval '30' day")

        if filters.price_range.data:
            if filters.price_range.data['title'] == '< 500':
                price = text("expected_close_price < 500")
            elif filters.price_range.data['title'] == '>= 500 and < 1000':
                price = text("expected_close_price >= 500 and expected_close_price < 1000")
            elif filters.price_range.data['title'] == '>= 1000 and < 10,000':
                price = text("expected_close_price >= 1000 and expected_close_price < 10000")
            elif filters.price_range.data['title'] == '>= 10,000 and < 50,000':
                price = text("expected_close_price >= 10000 and expected_close_price < 50000")
            elif filters.price_range.data['title'] == '>= 50,000 and < 100,000':
                price = text("expected_close_price >= 50000 and expected_close_price < 100000")
            elif filters.price_range.data['title'] == '>= 100,000':
                price = text("expected_close_price >= 100000")

        search = f'%{filters.txt_search.data}%'

        deal_stage = text("deal_stage_id=%s" % filters.deal_stages.data.id) if filters.deal_stages.data else True

        query = Deal.query.filter(or_(
            Deal.title.ilike(search)
        ) if search else True) \
            .filter(account) \
            .filter(contact) \
            .filter(price) \
            .filter(deal_stage) \
            .filter(owner) \
            .filter(date_today_filter) \
            .order_by(Deal.date_created.desc()) \
            .paginate(per_page=per_page, page=page)
    else:
        owner = True if current_user.role.name == 'admin' else text('Contact.owner_id=%d' % current_user.id)
        query = Deal.query \
            .filter(owner) \
            .order_by(Deal.date_created.desc()) \
            .paginate(per_page=per_page, page=page)

    if view_t == 'kanban':
        return render_template("deals/kanban_view.html", title="Deals View",
                               deals=query,
                               deal_stages=DealStage.query.order_by(DealStage.display_order.asc()).all())
    else:
        return render_template("deals/deals_list.html", title="Deals View", deals=query, filters=filters)


@deals.route("/deals/<int:deal_id>")
@login_required
@check_access('deals', 'view')
def get_deal_view(deal_id):
    deal = Deal.query.filter_by(id=deal_id).first()
    return render_template("deals/deal_view.html", title="Deal View", deal=deal)


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


@deals.route("/deals/update_stage/<int:deal_id>/<int:stage_id>")
@login_required
@check_access('deals', 'update')
def update_deal_stage_ajax(deal_id, stage_id):
    deal = Deal.query.filter_by(id=deal_id).first()
    deal.deal_stage_id = stage_id
    db.session.commit()
    return json.dumps({'success': True, 'message': 'Done'})


