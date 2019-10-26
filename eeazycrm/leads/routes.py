import pandas as pd
from sqlalchemy import or_

from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request

from eeazycrm import db
from .models import Lead
from .forms import NewLead, ImportLeads

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
                        country=form.country.data, source=form.lead_source.data, notes=form.notes.data)

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


@leads.route("/leads")
@login_required
@check_access('leads', 'view')
def get_leads_view():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('sq', None, type=str)
    search = f'%{search}%' if search else search

    leads_list = Lead.query\
        .filter(or_(
            Lead.first_name.ilike(search),
            Lead.last_name.ilike(search),
            Lead.email.ilike(search),
            Lead.company_name.ilike(search)
        ) if search else True)\
        .order_by(Lead.date_created.desc())\
        .paginate(per_page=per_page, page=page)

    return render_template("leads/leads_list.html", title="Leads View", leads=leads_list)


@leads.route("/leads/<int:lead_id>")
@login_required
@check_access('leads', 'view')
def get_lead_view(lead_id):
    lead = Lead.query.filter_by(id=lead_id).first()
    return render_template("leads/lead_view.html", title="View Lead", lead=lead)


@leads.route("/leads/convert/<int:lead_id>")
@login_required
@check_access('leads', 'view')
def convert_lead(lead_id):
    lead = Lead.query.filter_by(id=lead_id).first()
    return render_template("leads/lead_convert.html", title="Covert Lead", lead=lead)


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
