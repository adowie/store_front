from flask import abort, render_template,redirect,url_for,session
from flask_login import current_user, login_required

from . import home
from ..models import Company
from ..func_ import *
from ..api import fetchCustomers,fetchProductsBySearch,userItems


title_ = ""

# @home.route('/', methods=['GET', 'POST'])
# @login_required
# def land():
# 	"""
# 	Render the homepage template on the / route
# 	"""
# 	return redirect(url_for('home.dashboard'))
	
	

@home.route('/dashboard/')
@login_required
def dashboard():
	"""
	Render the dashboard template on the /dashboard route
	"""
	company = Company.query.filter_by(id=session["company"]["id"]).first()
	return render_template('home/index.html', title="Dashboard",company=company)


# @home.route('/admin/')
# @login_required
# def admin():
# 	"""
# 	Render the dashboard template on the /dashboard route
# 	"""
# 	company = Company.query.filter_by(id=session["company"]["id"]).first()
# 	return render_template('admin/index.html', title="Administrator",company=company)


@home.route("/search/", methods=['POST'])
@login_required
def search():
	company = Company.query.filter_by(id=session["company"]["id"]).first()
	search = DDOT(request.form.to_dict())
	error = {"error":"Your search produced no results."}

	if search.in_ and search.in_ == "customers":
		customers = fetchCustomers(search.for_)

		return render_template("search_.html",search=customers,in_="customer")
	elif search.in_ and search.in_ == "products":
		if int(search.for_) > 0: 
			products = fetchProductsBySearch(search) 
		else:
			products = userItems(current_user,"products",company.id)

		return render_template("search_.html",products=products,in_="product")
	elif search.in_ and search.in_ == "category":
		products = fetchProductsBySearch(search)
		return render_template("search_.html",products=products,in_="category_search")
	else:
		return render_template("search_.html",search=error)


@home.route("/widgets/", methods=['POST'])
@login_required
def widgetView():
	user = DDOT(request.form.to_dict())	
	company_types = getCompanyType()
	if user.widget == "add_company":
		owner = {"id":current_user.id,"name":current_user.fullname}
		return render_template("mods/company/company.html",error="",company_types=company_types,owner=owner)#,companies=companies,company=res
	elif user.widget == "add_company_type":
		return render_template("mods/company/company_type.html",error="",company_types=company_types)#,companies=companies,company=res
	# elif user.widget == "add_company_owner":
		# return render_template("company_owner.html",error="",company_types=company_types,customer=res)#,companies=companies,company=res
	else:
		return render_template("home/widget.html",error="Oops!... No %s widget was found to complete command. Please contact Support for assistance."%user.widget)#,companies=companies,company=res

	return render_template("mods/company/company.html",error="Oops!. Access Denied!. Log in as Administrator to access this feature.") #Invalid Administrator Username or Password. Please Enter your Administrator credentials to complete this command



@home.route('/conf/',methods=["POST","GET"])
def conf():
	error = ""
	conf_ = DDOT(request.form.to_dict())

	comp_id = session["company"]["id"]
	company_ =  getCompanyById(comp_id)
	ctypes = getCompanyType()

	if conf_:
		if int(conf_.conf_company):
			error = api.updateCompany(conf_,request.files["image_"])
			
	foot_note = company_.thank_note #"<b>Thank you for your business.</b><br/> Tell us about your experience and suggestions at <br /><b>%s</b>." % email
	head_note = "<span class='company_logo'><img src='/static/%s' alt='Set company logo' /></span><h3>%s</h3> <h5>%s</h5> <h6>%s</h6>" % (company_.logo,company_.name, company_.location , company_.contact)

	return render_template("home/config.html",title = title_+" | Company Configuration",user = current_user,year = year(),company = company_,company_types = ctypes,error = error,footer=foot_note,header=head_note)
