from flask import abort, render_template, redirect,url_for,request,flash,g,session
from flask_login import current_user, login_required, login_user, logout_user
from flask_admin import helpers, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView

class MyAdminIndexView(AdminIndexView):
	@expose('/')
	def index(self):
		if not current_user.is_authenticated:
			return redirect(url_for('.login_view'))
		return super(MyAdminIndexView, self).index()

	@expose('/login/', methods=('GET', 'POST'))
	def login_view(self):
		# handle user login
		from app import db, login_manager
		from .models import User

		form = request.form
		if form and 'login' in form:
			user_ = User.query.filter_by(email=form['email'],is_admin=True).first()
			if user_ and user_.verify_password(form['key']):
				print("verified")
				user_.update_last_login()
				login_user(user_, remember=False)
				user_.update_is_logged_in(1)
				return redirect(url_for('.index'))
			else:
				flash("Incorrect access token. If this error persist please contact your systems admin.","error")
		return render_template('admin_/login.html', title="OSFO | Login",form=form)

	@expose('/logout/', methods=('GET', 'POST'))
	def logout_view(self):
		# handle user login
		logout_user()
		return redirect(url_for('admin.login_view'))

	