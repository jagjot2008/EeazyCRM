from flask import request, session
from flask_login import current_user
from sqlalchemy import text
from eeazycrm.users.models import User
from eeazycrm.accounts.models import Account
from eeazycrm.contacts.models import Contact


class CommonFilters:

    @staticmethod
    def set_owner(filters, module, key):
        if not module or not filters or not key:
            return None

        if request.method == 'POST':
            if current_user.is_admin:
                if filters.assignees.data:
                    owner = text('%s.owner_id=%d' % (module, filters.assignees.data.id))
                    session[key] = filters.assignees.data.id
                else:
                    session.pop(key, None)
                    owner = True
            else:
                owner = text('%s.owner_id=%d' % (module, current_user.id))
                session[key] = current_user.id
        else:
            if key in session:
                owner = text('%s.owner_id=%d' % (module, session[key]))
                filters.assignees.data = User.get_by_id(session[key])
            else:
                owner = True if current_user.is_admin else text('%s.owner_id=%d' % (module, current_user.id))
        return owner

    @staticmethod
    def set_accounts(filters, module, key):
        if not module or not filters or not key:
            return None

        account = True
        if request.method == 'POST':
            if filters.accounts.data:
                account = text('%s.account_id=%d' % (module, filters.accounts.data.id))
                session[key] = filters.accounts.data.id
            else:
                session.pop(key, None)
        else:
            if key in session:
                account = text('%s.account_id=%d' % (module, session[key]))
                filters.accounts.data = Account.get_account(session[key])
        return account

    @staticmethod
    def set_contacts(filters, module, key):
        if not module or not filters or not key:
            return None

        contact = True
        if request.method == 'POST':
            if filters.contacts.data:
                contact = text('%s.contact_id=%d' % (module, filters.contacts.data.id))
                session[key] = filters.contacts.data.id
            else:
                session.pop(key, None)
        else:
            if key in session:
                contact = text('%s.contact_id=%d' % (module, session[key]))
                filters.contacts.data = Contact.get_contact(session[key])
        return contact

    @staticmethod
    def set_search(filters, key):
        search = None
        if request.method == 'POST':
            search = filters.txt_search.data
            session[key] = search

        if key in session:
            filters.txt_search.data = session[key]
            search = session[key]
        return search