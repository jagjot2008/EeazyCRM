from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request, Blueprint, session
import json
from wtforms import Label
from sqlalchemy import or_, text
from datetime import date, timedelta

from eeazycrm import db
from .models import Contact
from eeazycrm.common.paginate import Paginate
from eeazycrm.common.filters import CommonFilters
from .forms import NewContact, FilterContacts, filter_contacts_adv_filters_query
from eeazycrm.users.utils import upload_avatar

from eeazycrm.rbac import check_access

contacts = Blueprint('contacts', __name__)


def set_filters(f_id, module):
    today = date.today()
    filter_d = True
    if f_id == 1:
        filter_d = text("Date(%s.date_created)='%s'" % (module, today))
    elif f_id == 2:
        filter_d = text("Date(%s.date_created)='%s'" % (module, (today - timedelta(1))))
    elif f_id == 3:
        filter_d = text("Date(%s.date_created) > current_date - interval '7' day" % module)
    elif f_id == 4:
        filter_d = text("Date(%s.date_created) > current_date - interval '30' day" % module)
    return filter_d


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
            filters.advanced_user.data = filter_contacts_adv_filters_query()[session[key] - 1]
    return filter_d


def reset_contacts_filters():
    if 'contacts_owner' in session:
        session.pop('contacts_owner', None)
    if 'contacts_search' in session:
        session.pop('contacts_search', None)
    if 'contacts_acc_owner' in session:
        session.pop('contacts_acc_owner', None)
    if 'contacts_date_created' in session:
        session.pop('contacts_date_created', None)


@contacts.route("/contacts", methods=['GET', 'POST'])
@login_required
@check_access('contacts', 'view')
def get_contacts_view():
    filters = FilterContacts()
    search = CommonFilters.set_search(filters, 'contacts_search')
    owner = CommonFilters.set_owner(filters, 'Contact', 'contacts_owner')
    account = CommonFilters.set_accounts(filters, 'Contact', 'contacts_acc_owner')
    advanced_filters = set_date_filters(filters, 'Contact', 'contacts_date_created')

    query = Contact.query.filter(or_(
            Contact.first_name.ilike(f'%{search}%'),
            Contact.last_name.ilike(f'%{search}%'),
            Contact.email.ilike(f'%{search}%'),
            Contact.phone.ilike(f'%{search}%'),
            Contact.mobile.ilike(f'%{search}%'),
            Contact.address_line.ilike(f'%{search}%'),
            Contact.addr_state.ilike(f'%{search}%'),
            Contact.addr_city.ilike(f'%{search}%'),
            Contact.post_code.ilike(f'%{search}%')
        ) if search else True)\
        .filter(account) \
        .filter(owner) \
        .filter(advanced_filters) \
        .order_by(Contact.date_created.desc())

    return render_template("contacts/contacts_list.html", title="Contacts View",
                           contacts=Paginate(query=query), filters=filters)


@contacts.route("/contacts/acc/<int:account_id>")
@login_required
@check_access('contacts', 'view')
def get_account_contacts(account_id):
    items = Contact.query\
        .filter_by(account_id=account_id)\
        .order_by(Contact.date_created.desc())\
        .all()

    d = []
    for item in items:
        f = {'id': item.id, 'name': item.get_contact_name()}
        d.append(f)
    return json.dumps(d)


@contacts.route("/contacts/new", methods=['GET', 'POST'])
@login_required
@check_access('contacts', 'create')
def new_contact():
    form = NewContact()
    if request.method == 'POST':
        if form.validate_on_submit():
            contact = Contact(first_name=form.first_name.data,
                              last_name=form.last_name.data,
                              email=form.email.data,
                              phone=form.phone.data,
                              mobile=form.mobile.data,
                              address_line=form.address_line.data,
                              addr_state=form.addr_state.data,
                              addr_city=form.addr_city.data,
                              post_code=form.post_code.data,
                              country=form.country.data,
                              notes=form.notes.data)

            contact.account = form.accounts.data

            if form.avatar.data:
                picture_file = upload_avatar(contact, form.avatar.data)
                contact.avatar = picture_file

            if current_user.is_admin:
                contact.contact_owner = form.assignees.data
            else:
                contact.contact_owner = current_user

            db.session.add(contact)
            db.session.commit()
            flash('Contact has been successfully created!', 'success')
            return redirect(url_for('contacts.get_contacts_view'))
        else:
            print(form.errors)

            flash('Your form has errors! Please check the fields', 'danger')
    return render_template("contacts/new_contact.html", title="New Contact", form=form)


@contacts.route("/contacts/edit/<int:contact_id>", methods=['GET', 'POST'])
@login_required
@check_access('contacts', 'update')
def update_contact(contact_id):
    contact = Contact.get_contact(contact_id)
    if not contact:
        return redirect(url_for('contacts.get_contacts_view'))

    form = NewContact()
    if request.method == 'POST':
        if form.validate_on_submit():
            contact.first_name = form.first_name.data
            contact.last_name = form.last_name.data
            contact.email = form.email.data
            contact.phone = form.phone.data
            contact.mobile = form.mobile.data
            contact.address_line = form.address_line.data
            contact.addr_state = form.addr_state.data
            contact.addr_city = form.addr_city.data
            contact.post_code = form.post_code.data
            contact.country = form.country.data
            contact.contact_owner = form.assignees.data
            contact.account = form.accounts.data
            contact.notes = form.notes.data
            db.session.commit()
            flash('The contact has been successfully updated', 'success')
            return redirect(url_for('contacts.get_contact_view', contact_id=contact.id))
        else:
            print(form.errors)
            flash('Contact update failed! Form has errors', 'danger')
    elif request.method == 'GET':
        form.first_name.data = contact.first_name
        form.last_name.data = contact.last_name
        form.email.data = contact.email
        form.phone.data = contact.phone
        form.mobile.data = contact.mobile
        form.address_line.data = contact.address_line
        form.addr_state.data = contact.addr_state
        form.addr_city.data = contact.addr_city
        form.post_code.data = contact.post_code
        form.country.data = contact.country
        form.assignees.data = contact.contact_owner
        form.accounts.data = contact.account
        form.notes.data = contact.notes
        form.submit.label = Label('update_contact', 'Update Contact')
    return render_template("contacts/new_contact.html", title="Update Contact", form=form)


@contacts.route("/contacts/<int:contact_id>")
@login_required
@check_access('contacts', 'view')
def get_contact_view(contact_id):
    contact = Contact.query.filter_by(id=contact_id).first()
    return render_template("contacts/contact_view.html", title="View Contact", contact=contact)


@contacts.route("/contacts/del/<int:contact_id>")
@login_required
@check_access('contacts', 'delete')
def delete_contact(contact_id):
    Contact.query.filter_by(id=contact_id).delete()
    db.session.commit()
    flash('Contact removed successfully!', 'success')
    return redirect(url_for('contacts.get_contacts_view'))


@contacts.route("/contacts/reset_filters")
@login_required
@check_access('contacts', 'view')
def reset_filters():
    reset_contacts_filters()
    return redirect(url_for('contacts.get_contacts_view'))
