from flask import render_template
from functools import wraps
from flask_login import current_user
from eeazycrm.users.models import Resource, Role


class NullRBACRowException(Exception):
    pass


class RBACActionNotFoundException(Exception):
    pass


def is_allowed(role_id, resource, action):
    row = Role.query \
        .with_entities(
            Role.id,
            Resource.can_view,
            Resource.can_edit,
            Resource.can_create,
            Resource.can_delete) \
        .filter_by(id=role_id) \
        .join(Role.resources) \
        .filter_by(name=resource) \
        .first()

    if not row:
        raise NullRBACRowException

    if action == 'view':
        return row.can_view
    elif action == 'create':
        return row.can_create
    elif action == 'update':
        return row.can_edit
    elif action == 'remove':
        return row.can_delete
    else:
        raise RBACActionNotFoundException


def check_access(resource, action):
    def decorator(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin and not current_user.role:
                return render_template("no_access.html", title="Access Not Allowed")
            if current_user.is_admin:
                return function(*args, **kwargs)
            elif not current_user.is_admin and current_user.role:
                try:
                    if not is_allowed(current_user.role_id, resource, action):
                        return render_template("no_access.html", title="Access Not Allowed")
                    else:
                        return function(*args, **kwargs)
                except NullRBACRowException:
                    print("NullRBACRowException: Query failed for RBAC operation")
                except RBACActionNotFoundException:
                    print("RBACActionNotFoundException: Action not found")
        return decorated_function
    return decorator


def is_admin(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        if current_user.is_admin:
            return function(*args, **kwargs)
        else:
            return render_template("no_access.html", title="Access Not Allowed")
    return decorator
