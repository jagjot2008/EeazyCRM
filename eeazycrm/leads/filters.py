from flask import session, request
from flask_login import current_user
from .forms import filter_leads_adv_filters_admin_query, filter_leads_adv_filters_user_query
from datetime import date, timedelta
from sqlalchemy import text
from .models import LeadSource, LeadStatus


def set_filters(f_id):
    today = date.today()
    filter_d = True
    if f_id == 1:
        filter_d = text('Lead.owner_id IS NULL')
    elif f_id == 2:
        filter_d = text("date(Lead.date_created)='%s'" % today)
    elif f_id == 3:
        filter_d = text("date(Lead.date_created)='%s'" % (today - timedelta(1)))
    elif f_id == 4:
        filter_d = text("date(Lead.date_created) > current_date - interval '7' day")
    elif f_id == 5:
        filter_d = text("date(Lead.date_created) > current_date - interval '30' day")
    return filter_d


def assign_filter(filter_obj, key):
    filter_d = True
    if filter_obj.data:
        filter_d = set_filters(filter_obj.data['id'])
        session[key] = filter_obj.data['id']
    else:
        if key in session:
            session.pop(key, None)
    return filter_d


def set_date_filters(filters, key):
    filter_d = True
    if request.method == 'POST':
        if current_user.role.name == 'admin':
            filter_d = assign_filter(filters.advanced_admin, key)
        else:
            filter_d = assign_filter(filters.advanced_user, key)
    else:
        if key in session:
            filter_d = set_filters(session[key])
            if current_user.role.name == 'admin':
                filters.advanced_admin.data = filter_leads_adv_filters_admin_query()[session[key] - 1]
            else:
                filters.advanced_user.data = filter_leads_adv_filters_user_query()[session[key] - 1]
    return filter_d
