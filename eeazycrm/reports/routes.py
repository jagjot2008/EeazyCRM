from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template
from sqlalchemy import func, text
from eeazycrm.deals.models import Deal, DealStage
from eeazycrm.accounts.models import Account
from eeazycrm.users.models import User
from eeazycrm.rbac import is_admin

from functools import reduce

reports = Blueprint('reports', __name__)


@reports.route("/reports/deals")
@login_required
def deal_reports():
    return render_template("reports/reports.html", title="Reports")


@reports.route("/reports/deal_stages")
@login_required
def deal_stages():
    if current_user.is_admin:
        query = Deal.query \
            .with_entities(
                DealStage.stage_name.label('stage_name'),
                func.sum(Deal.expected_close_price).label('total_price'),
                func.count(Deal.id).label('total_count')
            ) \
            .join(Deal.deal_stage) \
            .group_by(DealStage.stage_name) \
            .order_by(text('total_price DESC'))
    else:
        query = Deal.query \
            .with_entities(
                DealStage.stage_name.label('stage_name'),
                func.sum(Deal.expected_close_price).label('total_price'),
                func.count(Deal.id).label('total_count')
            ) \
            .join(Deal.deal_stage) \
            .group_by(DealStage.stage_name, Deal.owner_id) \
            .having(Deal.owner_id == current_user.id) \
            .order_by(text('total_price DESC'))

    return render_template("reports/deals_stages.html",
                           title="Reports: Deal Stages", deals=query.all())


@reports.route("/reports/deals_closed")
@login_required
def deals_closed():
    if current_user.is_admin:
        query = Deal.query \
            .with_entities(
                Account.name.label('account_name'),
                DealStage.stage_name.label('stage_name'),
                func.sum(Deal.expected_close_price).label('total_price'),
                func.count(Deal.id).label('total_count')
            ) \
            .join(Deal.account, Deal.deal_stage) \
            .group_by(Account.name, DealStage.stage_name) \
            .order_by(text('stage_name'))
    else:
        query = Deal.query \
            .with_entities(
                Account.name.label('account_name'),
                DealStage.stage_name.label('stage_name'),
                func.sum(Deal.expected_close_price).label('total_price'),
                func.count(Deal.id).label('total_count')
            ) \
            .join(Deal.account, Deal.deal_stage) \
            .group_by(Account.name, DealStage.stage_name, Deal.owner_id) \
            .having(Deal.owner_id == current_user.id) \
            .order_by(text('stage_name'))

    stages = []
    data = []
    rows = query.all()
    if len(rows) > 0:
        for d in rows:
            if d[1] not in stages:
                stages.append(d[1])
                data.append({
                    'stage_name': d[1],
                    'accounts_count': len([x[1] for x in rows if x[1] == d[1]]),
                    'rows': [(x[0], x[2], x[3]) for x in rows if x[1] == d[1]]
                })

    return render_template("reports/deals_closed.html",
                           title="Reports: Deals Stages by Accounts", deals=data)


def get_users_deals():
    users_list = Deal.query \
        .with_entities(
            Deal.owner_id.label('owner'),
            User.first_name,
            User.last_name,
            DealStage.stage_name,
            func.sum(Deal.expected_close_price).label('total_price')
        ) \
        .filter(DealStage.stage_name.in_(['Closed - Won', 'Closed - Lost'])) \
        .join(Deal.owner, Deal.deal_stage) \
        .group_by(Deal.owner_id, User.first_name, User.last_name, DealStage.stage_name) \
        .order_by(text('owner'))

    won_list = [x for x in users_list.all() if x.stage_name == 'Closed - Won']
    lost_list = [x for x in users_list.all() if x.stage_name == 'Closed - Lost']
    return won_list, lost_list


@reports.route("/reports/deal_stage_by_users")
@login_required
@is_admin
def deal_stage_by_users():
    query = Deal.query \
        .with_entities(
            Deal.owner_id.label('owner'),
            User.first_name,
            User.last_name,
            DealStage.stage_name.label('stage_name'),
            func.sum(Deal.expected_close_price).label('total_price'),
            func.count(Deal.id).label('total_count')
        ) \
        .join(Deal.owner, Deal.deal_stage) \
        .group_by(Deal.owner_id, User.first_name, User.last_name, DealStage.stage_name) \
        .order_by(text('owner'))

    users = []
    data = []
    rows = query.all()
    if len(rows) > 0:
        for d in rows:
            if d[0] not in users:
                users.append(d[0])
                data.append({
                    'owner': f'{d[1]} {d[2]}',
                    'count': len([x[3] for x in rows if x[0] == d[0]]),
                    'rows': [(x[3], x[4], x[5]) for x in rows if x[0] == d[0]],
                    'total_cost': reduce(lambda a, b: a + b, [x[4] for x in rows if x[0] == d[0]]),
                    'total_qty': reduce(lambda a, b: a + b, [x[5] for x in rows if x[0] == d[0]])
                })

    return render_template("reports/deals_stage_by_users.html",
                           title="Reports: Deal Stages by Users",
                           deals=data,
                           deals_closed=get_users_deals())


@reports.route("/reports/deal_closed_by_date")
@login_required
def deal_closed_by_date():
    query = Deal.query \
        .with_entities(
            Deal.owner_id.label('owner'),
            User.first_name,
            User.last_name,
            DealStage.stage_name,
            Deal.expected_close_price.label('total_price')
        ) \
        .filter(DealStage.stage_name.in_(['Closed - Won', 'Closed - Lost'])) \
        .join(Deal.owner, Deal.deal_stage) \
        .group_by(
            Deal.owner_id,
            User.first_name,
            User.last_name,
            DealStage.stage_name,
            Deal.expected_close_date,
            Deal.expected_close_price) \
        .order_by(text('owner'))

    return render_template("reports/deals_closed_by_time.html",
                           title="Reports: Deal Stages by Users",
                           deals=data,
                           deals_closed=get_users_deals())
