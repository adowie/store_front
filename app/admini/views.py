from flask import abort, render_template, redirect,url_for,request,flash,g
from sqlalchemy.exc import InvalidRequestError, IntegrityError, SQLAlchemyError, DataError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required, login_user
from app import db, admin, login_manager
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import FileField, HiddenField
from wtforms.form import Form
from random import randrange
from . import admini
from ..models import *
import simplejson as json

db_sess = db.session


class UserView(ModelView):
	column_exclude_list = []
	column_searchable_list = ['fullname', 'email']
	form_excluded_columns = ['notifications','is_logged_in','access', 'company', 'sessions', 'orders', 'customer', 'lineup']
	def on_model_change(self, form, model, is_created):
		model.password_ = generate_password_hash(model.password)

	def is_accessible(self):
		if not current_user.is_authenticated:
			return False
		
		return role_master(current_user,"user")
		

class PlanView(ModelView):
	column_exclude_list = ['company']
	form_excluded_columns = ['company']
	def is_accessible(self):
		if not current_user.is_authenticated:
			return False
		return role_master(current_user,"plan")
		

class CompanyView(ModelView):
	column_searchable_list = ['name', 'email']
	column_exclude_list = ['categories', 'products', 'sessions', 'favourites', 'orders', 'line', 'pos']
	form_excluded_columns = ['categories', 'products', 'sessions', 'favourites', 'orders', 'line', 'pos']
	def is_accessible(self):
		if not current_user.is_authenticated:
			return False
		return role_master(current_user,"company")
		

class CategoryView(ModelView):
	can_export = True
	form_excluded_columns = ['products','companies']
	column_exclude_list = ['products','companies']
	def is_accessible(self):
		if not current_user.is_authenticated:
			return False
		return role_master(current_user,"category")
		

class ProductView(ModelView):
	form_excluded_columns = ['uoms','variants','orderline','favourites','images']
	column_exclude_list = ['variants','orderline','favourites','images']
	def is_accessible(self):
		if not current_user.is_authenticated:
			return False
		return role_master(current_user,"product")
		

class CustomerView(ModelView):
	form_excluded_columns = ['orders','fav_companies','fav_products']
	column_exclude_list = ['orders','fav_companies','fav_products']
	def is_accessible(self):
		if not current_user.is_authenticated:
			return False
		return role_master(current_user,"customer")
		

class CompanyTypeView(ModelView):
	form_excluded_columns = ['companies','categories']
	def is_accessible(self):
		if not current_user.is_authenticated:
			return False
		return role_master(current_user,"company_type")
			

class CompanyCategoryView(ModelView):
	def is_accessible(self):
		if not current_user.is_authenticated:
			return False
		return role_master(current_user,"company_category")
			

class CategoryProductView(ModelView):
	def is_accessible(self):
		if not current_user.is_authenticated:
			return False
		return role_master(current_user,"category_product")
			

class ProductPhotoView(ModelView):
	def is_accessible(self):
		if not current_user.is_authenticated:
			return False
		return role_master(current_user,"product_photo")
			

class NotificationView(ModelView):
	def is_accessible(self):
		if not current_user.is_authenticated:
			return False
		return role_master(current_user,"notification")
			

class OrderView(ModelView):
	def is_accessible(self):
		if not current_user.is_authenticated:
			return False
		return role_master(current_user,"order")
			

def role_master(user,module):
	if user.is_super_admin:
		return True
	return False

admin.add_view(UserView(User,db_sess))
admin.add_view(PlanView(Plan,db_sess))
admin.add_view(CompanyTypeView(CompanyType,db_sess))
admin.add_view(CompanyView(Company,db_sess))
admin.add_view(CustomerView(Customer,db_sess)) 
admin.add_view(CategoryView(Category,db_sess))
admin.add_view(CompanyCategoryView(CompanyCategory,db_sess))
admin.add_view(CategoryProductView(CategoryProduct,db_sess))
admin.add_view(ProductView(Product,db_sess))
admin.add_view(ProductPhotoView(ProductPhoto,db_sess))
admin.add_view(OrderView(Order,db_sess))
admin.add_view(NotificationView(Notification,db_sess))
