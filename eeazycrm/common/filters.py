from flask import request, session
from flask_login import current_user
from sqlalchemy import text
from eeazycrm.users.models import User


class CommonFilters:

    @staticmethod
    def set_owner(filters, module, key):
        if not module or not filters or not key:
            return None

        if request.method == 'POST':
            if current_user.role.name == 'admin':
                if filters.assignees.data:
                    owner = text('%s.owner_id=%d' % (module, filters.assignees.data.id))
                    session[key] = filters.assignees.data.id
                else:
                    owner = True
            else:
                owner = text('%s.owner_id=%d' % (module, current_user.id))
                session[key] = current_user.id
        else:
            if key in session:
                owner = text('%s.owner_id=%d' % (module, session[key]))
                filters.assignees.data = User.get_by_id(session[key])
            else:
                owner = True if current_user.role.name == 'admin' else text('%s.owner_id=%d' % (module, current_user.id))
        return owner

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