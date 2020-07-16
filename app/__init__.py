from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from .admin import MyAdminIndexView
import locale

locale.setlocale(locale.LC_ALL, 'en_US')

db = SQLAlchemy()
login_manager = LoginManager()
admin = Admin(name='OSFO Administrator', index_view=MyAdminIndexView(), template_mode='bootstrap3')

def server_error(e):
  return render_template('error/500.html'), 500

def page_not_found(e):
  return render_template('error/404.html'), 404 

def permission_denied(e):
  return render_template('error/403.html'), 403


def encript_(enc_str):
	from .func_ import encrypt_decrypt
	return encrypt_decrypt("e",enc_str)
		
def toTime(dt):
	from .func_ import datetimeToTime
	return datetimeToTime(dt)
	
def toMoney(n):
	if not n:
		return 0
	return locale.currency(float(n),grouping=True)

def calTax(taxable,ext_,tax_):
	if taxable:
		line_tax = float((tax_ / 100))
		return float(ext_) * line_tax
	return 0

def favourites(user):
	from .func_ import getFavourites
	return getFavourites(user)

def toDate(dt):
	from .func_ import datetimeToDate,today
	date_ = datetimeToDate(dt)
	if str(date_) == str(today()):
		return " "
	else:
		return date_

def parse_account_type(account):
	if account == 1:
		return "Customer"
	return "Business"

def ordinal(n):
	ord_ = ["st","nd","rd"]
	nth = ((n+90)%100-10)%10-1
	if nth < len(ord_):
		return f'{n}{ord_[nth]}'
	return f'{n}th'


def create_app():
	app = Flask(__name__)
	app.config.from_object('config')
	# app.config.from_pyfile('config.py')
	app.register_error_handler(404, page_not_found)
	app.register_error_handler(403, permission_denied)
	app.register_error_handler(500, server_error)
	app.jinja_env.globals.update(encript_=encript_)
	app.jinja_env.globals.update(toTime=toTime)
	app.jinja_env.globals.update(toMoney=toMoney)
	app.jinja_env.globals.update(toDate=toDate)	
	app.jinja_env.globals.update(calTax=calTax)	
	app.jinja_env.globals.update(ordinal=ordinal)	
	app.jinja_env.globals.update(favourites=favourites)	
	app.jinja_env.globals.update(parse_account_type=parse_account_type)	

	db.init_app(app)
	admin.init_app(app)

	login_manager.init_app(app)
	login_manager.login_message = "You must be logged in to access this resource."
	login_manager.login_view = 'osf.account'

	Bootstrap(app)
	
	migrate = Migrate(app, db)

	from app import views, models, api

	from .admini import admini as admin_blueprint
	app.register_blueprint(admin_blueprint)

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	from .mods import mods as mods_blueprint
	app.register_blueprint(mods_blueprint)

	from .home import home as home_blueprint
	app.register_blueprint(home_blueprint)

	from .pos import pos as pos_blueprint
	app.register_blueprint(pos_blueprint)

	from .osf import osf as osf_blueprint
	app.register_blueprint(osf_blueprint)
	

	return app