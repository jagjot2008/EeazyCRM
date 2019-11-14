import pandas as pd
from sqlalchemy import or_, text

from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request

from eeazycrm import db
from .models import Lead
from .forms import NewLead, ImportLeads, ConvertLead, FilterLeads
from datetime import date, timedelta

from eeazycrm.rbac import check_access

leads = Blueprint('leads', __name__)


@leads.route("/leads/new", methods=['GET', 'POST'])
@login_required
@check_access('leads', 'create')
def new_lead():
    form = NewLead()
    if request.method == 'POST':
        if form.validate_on_submit():
            lead = Lead(title=form.title.data,
                        first_name=form.first_name.data, last_name=form.last_name.data,
                        email=form.email.data, company_name=form.company.data,
                        address_line=form.address_line.data, addr_state=form.addr_state.data,
                        addr_city=form.addr_city.data, post_code=form.post_code.data,
                        country=form.country.data, source=form.lead_source.data,
                        status=form.lead_status.data, notes=form.notes.data)

            if current_user.role.name == 'admin':
                lead.owner = form.assignees.data
            else:
                lead.owner = current_user

            db.session.add(lead)
            db.session.commit()
            flash('New lead has been successfully created!', 'success')
            return redirect(url_for('leads.get_leads_view'))
        else:
            for error in form.errors:
                print(error)
            flash('Your form has errors! Please check the fields', 'danger')
    return render_template("leads/new_lead.html", title="New Lead", form=form)


@leads.route("/leads", methods=['GET', 'POST'])
@login_required
@check_access('leads', 'view')
def get_leads_view():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    filters = FilterLeads()
    today = date.today()

    if request.method == 'POST':
        lead_sources_list = tuple(map(lambda item: item.id, filters.lead_source.data))
        lead_status_list = tuple(map(lambda item: item.id, filters.lead_status.data))
        date_today_filter = True

        if current_user.role.name == 'admin':
            owner = text('Lead.owner_id=%d' % filters.assignees.data.id) if filters.assignees.data else True
        else:
            owner = text('Lead.owner_id=%d' % current_user.id)

        if filters.advanced_admin.data:
            if filters.advanced_admin.data['title'] == 'Unassigned':
                owner = text('Lead.owner_id IS NULL')
            elif filters.advanced_admin.data['title'] == 'Created Today':
                date_today_filter = text("Date(Lead.date_created)='%s'" % today)
            elif filters.advanced_admin.data['title'] == 'Created Yesterday':
                date_today_filter = text("Date(Lead.date_created)='%s'" % (today - timedelta(1)))
            elif filters.advanced_admin.data['title'] == 'Created In Last 7 Days':
                date_today_filter = text("Date(Lead.date_created) > current_date - interval '7' day")
            elif filters.advanced_admin.data['title'] == 'Created In Last 30 Days':
                date_today_filter = text("Date(Lead.date_created) > current_date - interval '30' day")

        if filters.advanced_user.data:
            if filters.advanced_user.data['title'] == 'Created Today':
                date_today_filter = text("Date(Lead.date_created)='%s'" % today)
            elif filters.advanced_user.data['title'] == 'Created Yesterday':
                date_today_filter = text("Date(Lead.date_created)='%s'" % (today - timedelta(1)))
            elif filters.advanced_user.data['title'] == 'Created In Last 7 Days':
                date_today_filter = text("Date(Lead.date_created) > current_date - interval '7' day")
            elif filters.advanced_user.data['title'] == 'Created In Last 30 Days':
                date_today_filter = text("Date(Lead.date_created) > current_date - interval '30' day")

        search = f'%{filters.txt_search.data}%'

        query = Lead.query \
            .filter(or_(
                Lead.title.ilike(search),
                Lead.first_name.ilike(search),
                Lead.last_name.ilike(search),
                Lead.email.ilike(search),
                Lead.company_name.ilike(search)
            ) if search else True) \
            .filter(Lead.lead_source_id.in_(lead_sources_list) if lead_sources_list else True) \
            .filter(Lead.lead_status_id.in_(lead_status_list) if lead_status_list else True) \
            .filter(owner) \
            .filter(date_today_filter) \
            .order_by(Lead.date_created.desc()) \
            .paginate(per_page=per_page, page=page)
    else:
        owner = True if current_user.role.name == 'admin' else text('Lead.owner_id=%d' % current_user.id)
        query = Lead.query \
            .filter(owner) \
            .order_by(Lead.date_created.desc()) \
            .paginate(per_page=per_page, page=page)
    return render_template("leads/leads_list.html", title="Leads View", leads=query, filters=filters)


@leads.route("/leads/<int:lead_id>")
@login_required
@check_access('leads', 'view')
def get_lead_view(lead_id):
    lead = Lead.query.filter_by(id=lead_id).first()
    return render_template("leads/lead_view.html", title="View Lead", lead=lead)


@leads.route("/leads/convert/<int:lead_id>", methods=['GET', 'POST'])
@login_required
@check_access('leads', 'view')
@check_access('accounts', 'create')
@check_access('contacts', 'create')
@check_access('deals', 'create')
def convert_lead(lead_id):
    lead = Lead.query.filter_by(id=lead_id).first()
    form = ConvertLead()
    form.account_name.data = lead.company_name
    form.account_email.data = lead.email

    if request.method == 'POST':
        if form.validate_on_submit():
            if form.use_account_information.data and form.use_contact_information.data:
                # create both account and contact

                pass
            elif form.use_account_information.data and not form.use_contact_information.data:
                # create account only (and contact if chosen from dropdown)
                if not form.account_name.data:
                    form.account_name.errors = ['Please enter account name']
                if not form.account_name.data:
                    form.account_email.errors = ['Please enter account email']
            elif not form.use_account_information.data and form.use_contact_information.data:
                pass
                # create contact only (account dropdown must be selected)
            elif not form.use_account_information.data and not form.use_contact_information.data:
                # account must be selected in dropdown (and create contact if selected in dropdown)
                if not form.accounts.data:
                    form.accounts.errors = ['Please select an account']
                pass

            flash('Leads has been successfully converted!', 'success')
        else:
            flash('Your form has errors! Please check the fields', 'danger')
    else:
        form.title.data = lead.title
    return render_template("leads/lead_convert.html", title="Convert Lead", lead=lead, form=form)


@leads.route("/leads/import", methods=['GET', 'POST'])
def import_bulk_leads():
    form = ImportLeads()
    if request.method == 'POST':
        ind = 0
        if form.validate_on_submit():
            data = pd.read_csv(form.csv_file.data)

            for _, row in data.iterrows():
                lead = Lead(first_name=row['first_name'], last_name=row['last_name'],
                            email=row['email'], company_name=row['company_name'])
                lead.owner = current_user
                if form.lead_source.data:
                    lead.source = form.lead_source.data
                db.session.add(lead)
                ind = ind + 1

            db.session.commit()
            flash(f'{ind} new lead(s) has been successfully imported!', 'success')
        else:
            flash('Your form has errors! Please check the fields', 'danger')
    return render_template("leads/leads_import.html", title="Import Leads", form=form)
