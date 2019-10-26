from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request

from eeazycrm import db

from eeazycrm.rbac import check_access

accounts = Blueprint('accounts', __name__)

