from flask import Blueprint, session
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request
from sqlalchemy import or_
import json
from wtforms import Label

from eeazycrm import db
from .models import Deal, DealStage
from eeazycrm.common.paginate import Paginate
from eeazycrm.common.filters import CommonFilters
from eeazycrm.accounts.models import Account
from .forms import NewDeal, FilterDeals
from .filters import set_date_filters, set_price_filters, set_deal_stage_filters

from eeazycrm.rbac import check_access

deals = Blueprint('deals', __name__)


def reset_deal_filters():
    if 'deals_owner' in session:
        session.pop('deals_owner', None)
    if 'deals_search' in session:
        session.pop('deals_search', None)
    if 'deals_acc_owner' in session:
        session.pop('deals_acc_owner', None)
    if 'deals_contacts_owner' in session:
        session.pop('deals_contacts_owner', None)
    if 'deals_date_created' in session:
        session.pop('deals_date_created', None)
    if 'deal_price' in session:
        session.pop('deal_price', None)
    if 'deal_stage' in session:
        session.pop('deal_stage', None)


@deals.route("/deals", methods=['GET', 'POST'])
@login_required
@check_access('deals', 'view')
def get_deals_view():
    view_t = request.args.get('view_t', 'list', type=str)
    filters = FilterDeals()

    search = CommonFilters.set_search(filters, 'deals_search')
    owner = CommonFilters.set_owner(filters, 'Deal', 'deals_owner')
    account = CommonFilters.set_accounts(filters, 'Deal', 'deals_acc_owner')
    contact = CommonFilters.set_contacts(filters, 'Deal', 'deals_contacts_owner')
    advanced_filters = set_date_filters(filters, 'Deal', 'deals_date_created')
    price_filters = set_price_filters(filters, 'deal_price')
    deal_stage_filters = set_deal_stage_filters(filters, 'deal_stage')

    query = Deal.query.filter(or_(
        Deal.title.ilike(f'%{search}%')
    ) if search else True) \
        .filter(account) \
        .filter(contact) \
        .filter(price_filters) \
        .filter(deal_stage_filters) \
        .filter(owner) \
        .filter(advanced_filters) \
        .order_by(Deal.date_created.desc())

    if view_t == 'kanban':
        return render_template("deals/kanban_view.html", title="Deals View",
                               deals=query.all(),
                               deal_stages=DealStage.query.order_by(DealStage.display_order.asc()).all(),
                               filters=filters)
    else:
        return render_template("deals/deals_list.html", title="Deals View",
                               deals=Paginate(query), filters=filters)


@deals.route("/deals/<int:deal_id>")
@login_required
@check_access('deals', 'view')
def get_deal_view(deal_id):
    deal = Deal.query.filter_by(id=deal_id).first()
    print(deal.account, deal.contact)
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
            if deal.account:
                deal.contact = form.contacts.data
            deal.dealstage = form.deal_stages.data

            if current_user.is_admin:
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


@deals.route("/deals/edit/<int:deal_id>", methods=['GET', 'POST'])
@login_required
@check_access('deals', 'update')
def update_deal(deal_id):
    form = NewDeal()
    account = request.args.get('acc', None, type=int)
    if account:
        form.accounts.data = Account.get_account(account)

    deal = Deal.get_deal(deal_id)
    if not deal:
        return redirect(url_for('deals.get_deals_view'))

    if request.method == 'POST':
        if form.validate_on_submit():
            deal.title = form.title.data
            deal.expected_close_price = form.expected_close_price.data
            deal.expected_close_date = form.expected_close_date.data
            deal.deal_stage = form.deal_stages.data
            deal.deal_account = form.accounts.data
            if form.accounts.data:
                deal.contact = form.contacts.data

            if current_user.is_admin:
                deal.deal_owner = form.assignees.data

            deal.notes = form.notes.data
            db.session.commit()
            flash('The deal has been successfully updated', 'success')
            return redirect(url_for('deals.get_deal_view', deal_id=deal.id))
        else:
            print(form.errors)
            flash('Deal update failed! Form has errors', 'danger')
    elif request.method == 'GET':
        form.title.data = deal.title
        form.expected_close_price.data = deal.expected_close_price
        form.expected_close_date.data = deal.expected_close_date
        form.deal_stages.data = deal.deal_stage
        form.accounts.data = deal.account
        form.contacts.data = deal.contact
        print(deal.contact)
        form.assignees.data = deal.deal_owner
        form.notes.data = deal.notes
        form.submit.label = Label('update_deal', 'Update Deal')
    return render_template("deals/new_deal.html", title="Update Deal", form=form)


@deals.route("/deals/update_stage/<int:deal_id>/<int:stage_id>")
@login_required
@check_access('deals', 'update')
def update_deal_stage_ajax(deal_id, stage_id):
    deal = Deal.query.filter_by(id=deal_id).first()
    deal.deal_stage_id = stage_id
    db.session.commit()
    return json.dumps({'success': True, 'message': 'Done'})


@deals.route("/deals/reset_filters")
@login_required
@check_access('deals', 'view')
def reset_filters():
    reset_deal_filters()
    view_t = request.args.get('view_t', 'list', type=str)
    return redirect(url_for('deals.get_deals_view', view_t=view_t))

