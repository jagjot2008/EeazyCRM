from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, flash, url_for, redirect, request
from sqlalchemy.exc import IntegrityError

from eeazycrm import db, bcrypt
from eeazycrm.rbac import check_access, is_admin
from eeazycrm.settings.forms import AppConfigForm
from eeazycrm.settings.models import AppConfig

app_config = Blueprint('app_config', __name__)


@app_config.route("/app_config", methods=['GET', 'POST'])
@login_required
def test():
    form = AppConfigForm()
    app_cfg = AppConfig.query.first()
    form.default_currency.data = app_cfg.currency
    form.default_timezone.data = app_cfg.time_zone
    form.date_format.data = app_cfg.date_format
    form.address_format.data = app_cfg.address_format
    return render_template("settings/appconfig/index.html", title="Application Configuration",
                           form=form)
