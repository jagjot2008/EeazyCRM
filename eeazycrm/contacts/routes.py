from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request
from sqlalchemy import or_

from eeazycrm import db
from .models import Contact

from eeazycrm.rbac import check_access

contacts = Blueprint('contacts', __name__)


@contacts.route("/contacts")
@login_required
@check_access('contacts', 'view')
def get_contacts_view():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('sq', None, type=str)
    search = f'%{search}%' if search else search

    contacts_list = Contact.query\
        .filter(or_(
            Contact.name.ilike(search),
            Contact.website.ilike(search),
            Contact.email.ilike(search),
            Contact.address_line.ilike(search)
        ) if search else True)\
        .order_by(Contact.date_created.desc())\
        .paginate(per_page=per_page, page=page)

    return render_template("contacts/contacts_list.html", title="Contacts View", contacts=contacts_list)