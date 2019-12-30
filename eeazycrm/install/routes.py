from flask import render_template, flash, url_for, redirect, Blueprint
from eeazycrm import db
from flask import current_app

install = Blueprint('install', __name__)


@install.route("/")
@install.route("/install")
def installation():
    return render_template("install/start.html", title="Welcome to EeazyCRM Installation")


@current_app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('install.installation'))

