from flask import flash, redirect, render_template, url_for,request,session
from flask_login import login_required, login_user, logout_user,current_user

from . import auth
from .. import db
from ..api import *
from ..func_ import *
from .forms import LoginForm, RegistrationForm, RecoverForm, SetNewPasswordForm,CompanyForm


title_ = "OSFO"

def verify_view_access(view):
    """
    check and action that user has access to view
    """
    for access in current_user.views:
        if access.view.name == view:
            return

    abort(403)

@auth.route('/recover', defaults={'token':None}, methods=['GET', 'POST'] )
@auth.route('/recover/<token>', methods=['GET', 'POST'])
def recover(token):
    """
    Handle requests to the /recover route
    send a recovery link via email and update database with recover request
    """
    if token:
        form = SetNewPasswordForm()
        if form.validate_on_submit():
            res_ = resetUserPassword(form.password.data,token)
            if 'success' in res_:
                flash('Your account has been successfully recovered. You can now login.')
                return redirect(url_for('auth.login'))
            else:
                if "token" in res_:
                    return redirect(url_for('auth.login'))
                else:
                    flash("Error: %s" % res_["error"])

        return render_template('auth/recover.html', form=form)
    else:
        form = RecoverForm()   
        if form.validate_on_submit():
            # res_ = recoverUserAccount(form.email.data,"auth")
            user_.add_notification("recovery", "auth", user_.id, "Customer Account Recovery", form["email"], 0)
            flash("A recovery email has been sent to email provided. Check your email for instructions to recover your account","success")
            return redirect(url_for('auth.login'))
        # load registration template
        return render_template('auth/recover.html', form=form)


@auth.route('/login', methods=['GET','POST'])
def login():    
    form = LoginForm()
    if form.validate_on_submit():
        # check whether employee exists in the database and whether
        # the password entered matches the password in the database
        user_ = loginPOSUser(form)
        if user_ is not None:
            # log employee in
            login_user(user_, remember=form.remember_me.data)
            return redirect(url_for('auth.company'))
        # when login details are incorrect
        else:
            flash('Invalid email or password.')
    return render_template("auth/login.html",title=title_+" | Login",form=form)

@auth.route('/company', methods=['GET', 'POST'])
@login_required
def company():
    user_ = current_user
    form = CompanyForm()
    form.company.choices = [(0,"-------- Select --------")]+ [(c.id,c.name) for c in Company.query.all()]
    if form.validate_on_submit():
        company_id = int(form.company.data)
        if bool(company_id):
            company_ = Company.query.filter_by(id=company_id).first()
            _id = randomString(16)
            session["company"] = company_.as_dict()
            createUserSession(user_.id,_id,company_id)
            session["id"] = _id
            return redirect(url_for('home.dashboard'))
    return render_template("auth/company.html",title=title_+" | Company",form=form,user=user_)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add an employee to the database through the registration form
    """
    form = DDOT(request.form.to_dict());

    if form.register:
        res = createUser(form,"") 

        if "error" in res:
            form["error"] = res["error"]
        else:
            form["success"] = res["success"]

            return redirect(url_for('auth.login'))

    return render_template("auth/register.html",title=title_+" | Register",form=form,load="register")


@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log an employee out through the logout link
    """
    logout_user()
    flash('You have been successfully logged out.')

    # redirect to the login page
    return redirect(url_for('auth.login'))

