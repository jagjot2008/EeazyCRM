from flask import render_template, flash, url_for, redirect, Blueprint
from eeazycrm import db
from flask_login import login_required

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
@login_required
def home():
    return render_template("index.html", title="Dashboard")


@main.route("/create_db")
def create_db():
    db.create_all()
    flash('Database created successfully!', 'info')
    return redirect(url_for('main.home'))


@main.route("/about")
def about():
    return render_template("about.html", title="About")


@main.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title="Page Not Found", error=error), 404
