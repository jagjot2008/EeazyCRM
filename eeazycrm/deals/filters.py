from flask import session, request
from .forms import filter_deals_adv_filters_query, filter_deals_price_query
from datetime import date, timedelta
from sqlalchemy import text
from .models import DealStage


def set_filters(f_id, module):
    today = date.today()
    filter_d = True
    if f_id == 1:
        filter_d = text("current_timestamp > Deal.expected_close_date")
    elif f_id == 2:
        filter_d = text("current_timestamp <= Deal.expected_close_date OR "
                        "Date(Deal.expected_close_date) IS NULL")
    elif f_id == 3:
        filter_d = text("expected_close_date "
                        "BETWEEN date_trunc('day', current_timestamp) AND "
                        "date_trunc('day', current_timestamp) + "
                        "interval '1 day' - interval '1 second'")
    elif f_id == 4:
        filter_d = text("expected_close_date "
                        "BETWEEN date_trunc('day', current_timestamp) + interval '1 day' AND "
                        "date_trunc('day', current_timestamp) + interval '7 day' - interval '1 second'")
    elif f_id == 5:
        filter_d = text("expected_close_date "
                        "BETWEEN date_trunc('day', current_timestamp) + interval '1 day' AND "
                        "date_trunc('day', current_timestamp)"
                        " + interval '30 day' - interval '1 second'")
    elif f_id == 6:
        filter_d = text("date(%s.date_created)='%s'" % (module, today))
    elif f_id == 7:
        filter_d = text("date(%s.date_created)='%s'" % (module, (today - timedelta(1))))
    elif f_id == 8:
        filter_d = text("date(%s.date_created) > current_date - interval '7' day" % module)
    elif f_id == 9:
        filter_d = text("date(%s.date_created) > current_date - interval '30' day" % module)
    return filter_d


def set_p_filters(f_id):
    price = True
    if f_id == 1:
        price = text("expected_close_price < 500")
    elif f_id == 2:
        price = text("expected_close_price >= 500 and expected_close_price < 1000")
    elif f_id == 3:
        price = text("expected_close_price >= 1000 and expected_close_price < 10000")
    elif f_id == 4:
        price = text("expected_close_price >= 10000 and expected_close_price < 50000")
    elif f_id == 5:
        price = text("expected_close_price >= 50000 and expected_close_price < 100000")
    elif f_id == 6:
        price = text("expected_close_price >= 100000")
    return price


def set_date_filters(filters, module, key):
    filter_d = True
    if request.method == 'POST':
        if filters.advanced_user.data:
            filter_d = set_filters(filters.advanced_user.data['id'], module)
            session[key] = filters.advanced_user.data['id']
        else:
            session.pop(key, None)
    else:
        if key in session:
            filter_d = set_filters(session[key], module)
            filters.advanced_user.data = filter_deals_adv_filters_query()[session[key] - 1]
    return filter_d


def set_price_filters(filters, key):
    filter_d = True
    if request.method == 'POST':
        if filters.price_range.data:
            filter_d = set_p_filters(filters.price_range.data['id'])
            session[key] = filters.price_range.data['id']
        else:
            session.pop(key, None)
    else:
        if key in session:
            filter_d = set_p_filters(session[key])
            filters.price_range.data = filter_deals_price_query()[session[key] - 1]
    return filter_d


def set_deal_stage_filters(filters, key):
    if not filters or not key:
        return None

    deal_stage = True
    if request.method == 'POST':
        if filters.deal_stages.data:
            deal_stage = text('Deal.deal_stage_id=%d' % filters.deal_stages.data.id)
            session[key] = filters.deal_stages.data.id
        else:
            session.pop(key, None)
    else:
        if key in session:
            deal_stage = text('Deal.deal_stage_id=%d' % session[key])
            filters.deal_stages.data = DealStage.get_deal_stage(session[key])
    return deal_stage
