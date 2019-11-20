from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template
from sqlalchemy import func, text
from eeazycrm.deals.models import Deal, DealStage

reports = Blueprint('reports', __name__)


@reports.route("/reports/deals")
@login_required
def deal_reports():
    return render_template("reports/deals.html", title="Deal Reports")


@reports.route("/reports/deals_closed")
@login_required
def deals_closed():
    deals = Deal.query \
        .with_entities(
            DealStage.stage_name.label('stage_name'),
            func.sum(Deal.expected_close_price).label('total_price'),
            func.count(Deal.id).label('total_count')
        ) \
        .join(Deal.deal_stage) \
        .group_by(DealStage.stage_name) \
        .having(Deal.owner_id == current_user.id if current_user.role.name != 'admin' else True) \
        .order_by(text('total_price DESC'))
    return render_template("reports/deals_stages.html",
                           title="Reports: Deal Stages", deals=deals.all())
