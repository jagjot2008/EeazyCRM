from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request, Blueprint
import json
from sqlalchemy import or_, text
from datetime import date, timedelta

from eeazycrm import db
from .models import Contact
from .forms import NewContact, FilterContacts
from eeazycrm.users.utils import upload_avatar

from eeazycrm.rbac import check_access

contacts = Blueprint('contacts', __name__)


@contacts.route("/contacts", methods=['GET', 'POST'])
@login_required
@check_access('contacts', 'view')
def get_contacts_view():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    filters = FilterContacts()

    if request.method == 'POST':
        today = date.today()
        date_today_filter = True
        if current_user.role.name == 'admin':
            owner = text('Contact.owner_id=%d' % filters.assignees.data.id) if filters.assignees.data else True
        else:
            owner = text('Contact.owner_id=%d' % current_user.id)

        account = text('Contact.account_id=%d' % filters.accounts.data.id) if filters.accounts.data else True

        if filters.advanced_user.data:
            if filters.advanced_user.data['title'] == 'Created Today':
                date_today_filter = text("Date(Contact.date_created)='%s'" % today)
            elif filters.advanced_user.data['title'] == 'Created Yesterday':
                date_today_filter = text("Date(Contact.date_created)='%s'" % (today - timedelta(1)))
            elif filters.advanced_user.data['title'] == 'Created In Last 7 Days':
                date_today_filter = text("Date(Contact.date_created) > current_date - interval '7' day")
            elif filters.advanced_user.data['title'] == 'Created In Last 30 Days':
                date_today_filter = text("Date(Contact.date_created) > current_date - interval '30' day")

        search = f'%{filters.txt_search.data}%'

        query = Contact.query.filter(or_(
            Contact.first_name.ilike(search),
            Contact.last_name.ilike(search),
            Contact.email.ilike(search),
            Contact.phone.ilike(search),
            Contact.mobile.ilike(search),
            Contact.address_line.ilike(search),
            Contact.addr_state.ilike(search),
            Contact.addr_city.ilike(search),
            Contact.post_code.ilike(search)
        ) if search else True) \
            .filter(account) \
            .filter(owner) \
            .filter(date_today_filter) \
            .order_by(Contact.date_created.desc()) \
            .paginate(per_page=per_page, page=page)
    else:
        owner = True if current_user.role.name == 'admin' else text('Contact.owner_id=%d' % current_user.id)
        query = Contact.query \
            .filter(owner) \
            .order_by(Contact.date_created.desc()) \
            .paginate(per_page=per_page, page=page)

    return render_template("contacts/contacts_list.html", title="Contacts View", contacts=query, filters=filters)


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

            if current_user.role.name == 'admin':
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
