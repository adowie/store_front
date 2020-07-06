# from flask import flash, redirect, render_template, url_for,request,session
# from flask_login import login_required, login_user, logout_user,current_user

# from .. import db
# from ..api import *
# from ..func_ import *
# import simplejson as json
# import locale



# locale.setlocale(locale.LC_ALL, 'en_US')
# title_ = "Teletta "
# empty_form = [1]

# @app.context_processor
# def utility_processor():
# 	def encript_(enc_str):
# 		enc_pass = cfg.encrypt_decrypt("e",enc_str)
# 		return enc_pass
# 	return dict(encript_=encript_)

# @app.context_processor
# def utility_processor():
# 	def toTime(dt):
# 		time_ = cfg.datetimeToTime(dt)
# 		return time_
# 	return dict(toTime=toTime)

# @app.context_processor
# def utility_processor():
# 	def toMoney(n):
# 		money_ =  locale.currency(n,grouping=True)
# 		return money_
# 	return dict(toMoney=toMoney)

# @app.context_processor
# def utility_processor():
# 	def toDate(dt):
# 		date_ = cfg.datetimeToDate(dt)
# 		if str(date_) == str(cfg.today()):
# 			return " "
# 		else:
# 			return date_
# 	return dict(toDate=toDate)

# @app.route('/logout')
# def logout():
# 	auth.Adminuser["isAuthenticated"] = False
# 	return redirect(url_for("login"))


# @app.route('/index')
# @app.route('/', methods=['GET','POST'])
# def login():	

# 	form = cfg.Map(request.form.to_dict());
# 	user_ = auth.authenticate(form.username,form.password,form)

# 	if form.login:
# 		if user_ and user_["isAuthenticated"]:
# 			if user_["in_company"] is None:
# 				user_ = auth.authenticate(form.username,form.password,form)
# 				return render_template("login.html",title=title_+" | Login",form=form,user=user_,load="login")
# 			else:
# 				if auth.Adminuser["session"] is None: 
# 					auth.Adminuser["session"] = api.createSession(user_)
# 				return render_template("index.html",title=title_+" | Home",year=cfg.year(),user=user_)
		
# 		return render_template("login.html",title=title_+" | Login",form=form,user=user_,load="login")

# 	else:
# 		if form.register:
# 			res = api.createUser(form,"") 

# 			if "error" in res:
# 				form["error"] = res["error"]
# 			else:
# 				form["success"] = res["success"]

# 			return render_template("login.html",title=title_+" | Register",form=form,load="register")

# 	return render_template("login.html",title=title_+" | Login",form=empty_form,user=user_,load="login")


# @app.route('/about')
# def about():
# 	form = LoginForm()

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		return render_template("about.html",title=title_+" | About",user=auth.Adminuser,year=cfg.year())
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/support')
# def support():

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		return render_template("support.html",title=title_+" | Support",user=auth.Adminuser,year=cfg.year())
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/customers')
# def customers():
# 	res = {"form":empty_form}
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		customers = api.getCustomersByCompany(auth.Adminuser["in_company"])
# 		companies = getCompany()
# 		return render_template("customers.html",title=title_+" | Customers",user=auth.Adminuser,year=cfg.year(),customers=customers,customer=res,companies=companies)
# 	else:
# 		return redirect(url_for("login"))
		

# @app.route("/search", methods=['POST'])
# def search():
# 	search = cfg.Map(request.form.to_dict())
# 	error = {"error":"Your search produced no results."}

# 	if search.in_ and search.in_ == "customers":
# 		customers = fetchCustomers(search.for_)

# 		return render_template("search_.html",search=customers,in_="customer")
# 	elif search.in_ and search.in_ == "products":
# 		products = fetchProductsBySearch(search)
	 
# 		return render_template("search_.html",products=products,in_="product")
#  	else:
#  		return render_template("search_.html",search=error)


# @app.route("/widgets", methods=['POST'])
# @login_required
# def widgetView():
# 	user = cfg.Map(request.form.to_dict())	
# 	company_types = getCompanyType()
# 	if user.widget == "add_company":
# 		owner = {"id":current_user.id,"name":current_user.fullname}
# 		return render_template("mods/company/company.html",error="",company_types=company_types,owner=owner)#,companies=companies,company=res
# 	elif user.widget == "add_company_type":
# 		return render_template("mods/company/company_type.html",error="",company_types=company_types)#,companies=companies,company=res
# 	# elif user.widget == "add_company_owner":
# 		# return render_template("company_owner.html",error="",company_types=company_types,customer=res)#,companies=companies,company=res
# 	else:
# 		return render_template("widget.html",error="Oops!... No %s widget was found to complete command. Please contact Support for assistance."%user.widget)#,companies=companies,company=res

# 	return render_template("mods/company/company.html",error="Oops!. Access Denied!. Log in as Administrator to access this feature.") #Invalid Administrator Username or Password. Please Enter your Administrator credentials to complete this command


# @app.route("/company/create",methods=["POST","GET"])
# def addCompany():
# 	form = request.form
# 	ajax = True if "ajax" in form else False

# 	if ajax:
# 		if auth.user:
# 			res = api.createCompany(form,"")
# 			user = auth.user.query.filter_by(id=auth.Adminuser["id"]).first()
# 			companies = user.companies #getCompany()
# 			ctypes = getCompanyType()

# 			ret = {}
# 			ret["result"] = {}
# 			ret["result"]["form"] = [res["form"]] if "form" in res else empty_form
# 			ret["result"]["types"] = [companies]
# 			ret["result"]["error"] = res["error"] if "error" in res else "success"

# 			if ret["result"]["error"] == "success":
# 				company_id = None

# 				for cmp_ in companies:
# 					if cmp_.name == form["name"]:
# 						company_id = cmp_.id

# 				access_ = {"user":user.id,"company":company_id,"role":1}
# 				error = auth.addUserAccess(cfg.Map(access_))
# 				print(error)
# 			# return json.dumps(res)
# 			return json.dumps(ret,default=lambda a: {'id':a.id,'name':a.name } )
# 		return redirect(url_for("login"))
# 	else:
# 		if auth.user:
# 			res = api.createCompany(form,request.files["image_"])

# 			user = auth.user.query.filter_by(id=auth.Adminuser["id"]).first()
# 			companies = user.companies #getCompany()
# 			ctypes = getCompanyType()
		
# 			if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 				return render_template("company.html",company_types=ctypes,companies=companies,company=res)
		
# 		return redirect(url_for("login"))


# @app.route("/company/view")
# def getCompany():
# 	company = api.getCompanies()
# 	return company
	


# @app.route("/company/type/view")
# def getCompanyType():
# 	companytype = api.getCompanyTypes()
# 	return companytype
	


# @app.route("/company/type/create",methods=["POST"])
# def addCompanyType():
# 	ret = {}
# 	ret["result"] = {}
# 	form = request.form
# 	res = api.createCompanyType(form)
# 	ctypes = getCompanyType()
	
# 	ret["result"]["form"] = [res["form"]] if "form" in res else empty_form
# 	ret["result"]["types"] = [ctypes]
# 	ret["result"]["error"] = res["error"] if "error" in res else "success"

# 	return json.dumps(ret,default=lambda a: {'id':a.id,'name':a.name } )
	

# @app.route('/conf',methods=["POST","GET"])
# def conf():
# 	error = ""
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		conf_ = cfg.Map(request.form.to_dict())

# 		comp_id = int(auth.Adminuser["in_company"])
# 		company_ =  api.getCompanyById(comp_id)
# 		ctypes = getCompanyType()

# 		if conf_:
# 			if int(conf_.conf_company):
# 				error = api.updateCompany(conf_,request.files["image_"])
				

# 		foot_note = company_.thank_note #"<b>Thank you for your business.</b><br/> Tell us about your experience and suggestions at <br /><b>%s</b>." % email
# 		head_note = "<span class='company_logo'><img src='static/%s' alt='Set company logo' /></span><h3>%s</h3> <h5>%s</h5> <h6>%s</h6>" % (company_.logo,company_.name, company_.location , company_.contact)

# 		return render_template("config.html",title = title_+" | Company Configuration",user = auth.Adminuser,year = cfg.year(),company = company_,company_types = ctypes,error = error,footer=foot_note,header=head_note)
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/conf/pos_',methods=["POST","GET"])
# def conf_pos():
# 	error = ""
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		return render_template("config_pos.html",title = title_+" | POS Configuration",user = auth.Adminuser,year = cfg.year(),error = error)
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/pos',methods=["GET","POST"])
# def pos():
# 	products = []
# 	session_ = []

# 	pos_ = cfg.Map(request.form.to_dict())
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		categories = getCategory()
# 		user = auth.user.query.filter_by(id=auth.Adminuser["id"]).first()

# 		pos_session = api.createPOSSession(auth.Adminuser)
# 		products = api.userItems(user,"products",auth.Adminuser["in_company"])
						
# 		if pos_session is not None:
# 			if len(pos_session.orders) < 1:
# 				session_ = api.createNewOrder(pos_session)
# 			else:
# 				session_ = pos_session

# 			return render_template("pos.html",title=title_+" | POS Session",user=auth.Adminuser,time=cfg.now_time(),categories=categories,products=products,pos=session_)
# 		else:
# 			return render_template("index.html",title=title_+" | Home",year=cfg.year(),user=user_,error="Oops!. Cannot create POS seesion for some wierd reason. Please contact support for assistance.")
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/pos/order/create',methods=["GET","POST"])
# def new_order():
# 	pos_ = cfg.Map(request.form.to_dict())
	
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		user = auth.user.query.filter_by(id=auth.Adminuser["id"]).first()

# 		session_ = api.createNewOrder(pos_)
# 		categories = getCategory()
# 		products = api.userItems(user,"products",auth.Adminuser["in_company"])

# 		return render_template("spos.html",title=title_+" | POS Session",user=auth.Adminuser,time=cfg.now_time(),categories=categories,products=products,pos=session_)
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/pos/order/customer/dialog',methods=["GET","POST"])
# def setCustomersDialog():
# 	pos = cfg.Map(request.form.to_dict()) 
# 	customers_ = api.getCustomersByCompany(pos.company)
# 	customer = api.getCustomerbyID(pos.customer,pos.company)
	
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		return render_template("pos_set_customer.html",order=pos.order_id,pos=pos.pos_,customers=customers_,customer=customer)
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/pos/order/products/search',methods=["GET","POST"])
# def setProductsDialog():
# 	pos = cfg.Map(request.form.to_dict()) 
# 	products_ = api.getProductsByName(pos)
		
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		return render_template("pos_set_products.html",order=pos.order_id,pos=pos.pos_,products=products_)
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/pos/order/payment',methods=["GET","POST"])
# def setPaymentDialog():
# 	pos = cfg.Map(request.form.to_dict()) 
# 	customers_ = api.getCustomersByCompany(pos.company)
# 	customer = api.getCustomerbyID(pos.customer,pos.company)
# 	order = api.getOrderById(pos)
# 	company = api.getCompanyById(pos.company)
# 	email = company.email if company.email is not None else "[** Set company email go to->setup->company setup tab **]" 
# 	name = company.name if company.name is not None else "[** Set company name go to->setup->company setup tab **]" 
# 	logo = company.logo if company.logo is not None else "/img/company/no_logo.png" 
# 	location = company.location if company.location is not None else "[** Set company location go to->setup->company setup tab **]" 
# 	contact = company.contact if company.contact is not None else "[** Set company contact go to->setup->company setup tab **]"

# 	payments = api.getOrderPayments(pos) 

# 	foot_note = company.thank_note #"<b>Thank you for your business.</b><br/> Tell us about your experience and suggestions at <br /><b>%s</b>." % email
# 	head_note = "<span class='company_logo'><img src='static/%s' alt='Set company logo' /></span><h3>%s</h3> <h5>%s</h5> <h6>%s</h6>" % (logo,name, location , contact)

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		return render_template("payment.html",payments=payments,order=order,pos=pos.pos_,customers=customers_,customer=customer,amount_due=pos.amount_due,header=head_note,footer=foot_note)
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/pos/order/payment/save',methods=["GET","POST"])
# def saveOrderPayment():
# 	order = cfg.Map(request.form.to_dict()) 
# 	payments = api.addPayment(order)

# 	return render_template("payments.html",payments=payments)
	


# @app.route('/pos/order/payment/remove',methods=["GET","POST"])
# def removeOrderPayment():
# 	line = cfg.Map(request.form.to_dict()) 
# 	payments = api.removePayment(line)

# 	return render_template("payments.html",payments=payments)
	

# @app.route('/pos/order/customer/set',methods=["GET","POST"])
# def setCustomer():
# 	cf = cfg.Map(request.form.to_dict()) 
	
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		user = auth.user.query.filter_by(id=auth.Adminuser["id"]).first()

# 		session_ = api.setPosOrderCustomer(cf)
# 		categories = getCategory()
# 		products = api.userItems(user,"products",auth.Adminuser["in_company"])

# 		return render_template("spos.html",title=title_+" | POS Session",user=auth.Adminuser,time=cfg.now_time(),categories=categories,products=products,pos=session_)
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/pos/order/cancel',methods=["GET","POST"])
# def cancel_order():
# 	order_ = cfg.Map(request.form.to_dict())
	
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		user = auth.user.query.filter_by(id=auth.Adminuser["id"]).first()

# 		session_ = api.removeOrder(order_)
# 		categories = getCategory()
# 		products = api.userItems(user,"products",auth.Adminuser["in_company"])

# 		return render_template("spos.html",title=title_+" | POS Session",user=auth.Adminuser,time=cfg.now_time(),categories=categories,products=products,pos=session_)
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/pos/orderline', methods=["POST"])
# def order():
# 	item_ = cfg.Map(request.form.to_dict())
	
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):	
# 		orderline = api.createOrderline(item_)
		
# 		user = auth.user.query.filter_by(id=auth.Adminuser["id"]).first()
# 		products = api.userItems(user,"products",auth.Adminuser["in_company"])
# 		categories = getCategory()
# 		session_ = api.createPOSSession(auth.Adminuser)

# 		return render_template("spos.html",title=title_+" | POS Session",user=auth.Adminuser,time=cfg.now_time(),categories=categories,products=products,pos=session_)
# 	else:
# 		return redirect(url_for("login"))#json.dumps({"error":"Authentication Error!"})
		


# @app.route('/pos/orderline/void', methods=["POST"])
# def void_line():
# 	line_ = cfg.Map(request.form.to_dict())

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		user_ = cfg.Map(auth.Adminuser)
# 		session_ = api.orderlineVoid(line_,user_)

# 		user = auth.user.query.filter_by(id=auth.Adminuser["id"]).first()
# 		products = api.userItems(user,"products",auth.Adminuser["in_company"])
# 		categories = getCategory()

# 		return render_template("spos.html",title=title_+" | POS Session",user=auth.Adminuser,time=cfg.now_time(),categories=categories,products=products,pos=session_)
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/pos/close')
# def pos_close():

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		return render_template("index.html",title=title_+" | Home",user=auth.Adminuser,year=cfg.year())
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/customer/add')
# def customerAdder():
# 	res = {"form":empty_form}
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		customers = api.getCustomersByCompany(auth.Adminuser["in_company"])
# 		companies = getCompany()
# 		return render_template("customer_adder.html",title=title_+" | Customers",user=auth.Adminuser,year=cfg.year(),customers=customers,customer=res,companies=companies)
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/customers/create', methods=['GET','POST'])
# def addCustomer():
# 	form = request.form
# 	ajax = True if "ajax" in form else False
	
# 	if ajax:
# 		res = api.createCustomer(form,"")
# 		customers = getCustomers()
		
# 		ret = {}
# 		ret["result"] = {}
# 		ret["result"]["form"] = [res["form"]] if res["form"] else empty_form
# 		ret["result"]["types"] = [customers]
# 		ret["result"]["error"] = res["error"] 

# 		return json.dumps(ret,default=lambda a: {'id':a.id,'name':a.name } )
# 	else:
# 		res = api.createCustomer(form,request.files["image_"])
# 		customers = getCustomers()
# 		if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 			return render_template("customer_adder.html",title=title_+" | Customers",user=auth.Adminuser,year=cfg.year(),customers=customers,customer=res)
# 		else:
# 			return redirect(url_for("login"))


# @app.route('/customers/remove',methods=['GET','POST'])
# def removeCustomer():
# 	form = request.form
# 	res = api.deleteCustomer(form)
# 	customers = getCustomers()

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		return render_template("customers.html",title=title_+" | Customers",user=auth.Adminuser,year=cfg.year(),customers=customers,customer=res)
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/customers/view')
# def getCustomers():
# 	customers = api.getCustomers()
# 	return customers
	

































# as been ported to mods/product/

# # [products routing]
# @app.route('/products', methods=['GET', 'POST'])
# def processProductRequest():
# 	products = []

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		user = auth.user.query.filter_by(id=auth.Adminuser["id"]).first()
# 		companies = user.companies #getCompany()

# 		if companies:
# 			for company in companies:
# 				if int(company.id) == int(auth.Adminuser["in_company"]):
# 					products = company.products
		
# 		categories = getCategory()
# 		uom = getUom()
# 		ptype = getProductType()

# 		res = {"form": empty_form}
# 		return render_template("products.html",title=title_+" | Products",user=auth.Adminuser,year=cfg.year(),products=products,product=res,categories=categories,uoms=uom,types=ptype,companies=companies)
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/products/add', methods=['GET','POST'])
# def productAdder():  
# 	products = []

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser):
# 		user = auth.user.query.filter_by(id=auth.Adminuser["id"]).first()
# 		companies = user.companies #getCompany()

# 		if companies:
# 			for company in companies:
# 				products = company.products
		
# 		categories = getCategory()
# 		uom = getUom()
# 		ptype = getProductType()

# 		res = {"form":[1]}

# 		return render_template("product_adder.html",title=title_+" | Products",user=auth.Adminuser,year=cfg.year(),products=products,product=res,categories=categories,uoms=uom,types=ptype,companies=companies)
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/products/create', methods=['GET','POST'])
# def addProduct():  
# 	form = request.form
		
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 

# 		res = api.createProduct(form,request.files["image_"]) 
# 		user = auth.user.query.filter_by(id=auth.Adminuser["id"]).first()
# 		companies = user.companies #getCompany()

# 		if companies:
# 			for company in companies:
# 				products = company.products
		
# 		categories = getCategory()
# 		uom = getUom()
# 		ptype = getProductType()


# 		return render_template("product_adder.html",title=title_+" | Products",user=auth.Adminuser,year=cfg.year(),products=products,product=res,categories=categories,uoms=uom,types=ptype,companies=companies)
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/products/type', methods=['GET','POST'])
# def ProductType():  
# 	ptype = getProductType()
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return render_template("product_type.html",title=title_+" | Product Types",user=auth.Adminuser,year=cfg.year(),types=ptype,type=[])
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/products/type/create', methods=['GET','POST'])
# def addProductType():  
# 	form = request.form
# 	res = api.createProductType(form) 
# 	ptype = getProductType()

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return render_template("product_type.html",title=title_+" | Product Types",user=auth.Adminuser,year=cfg.year(),types=ptype,type=res)
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/products/uom/view', methods=['GET'])
# def getProductType():
# 	ptype = api.getProductType()
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return ptype
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/products/uom', methods=['GET','POST'])
# def ProductUom():   
# 	uom = getUom()

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return render_template("product_uom.html",title=title_+" | Product Unit Of Measure",user=auth.Adminuser,year=cfg.year(),uoms=uom,uom=[])
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/products/uom/create', methods=['GET','POST'])
# def addProductUom():  
# 	form = request.form
# 	res = api.createUom(form) 
# 	uom = getUom()

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return render_template("product_uom.html",title=title_+" | Product Unit Of Measure",user=auth.Adminuser,year=cfg.year(),uoms=uom,uom=res)
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/products/uom/view', methods=['GET'])
# def getUom():
# 	uom = api.getUom()
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return uom
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/products/view', methods=['GET'])
# def getProduct():  
# 	products = api.getProducts()

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return products
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/products/category/view', methods=['GET'])
# def getCategory():  
# 	category = api.getCategories()

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return category
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/products/remove', methods=['POST'])
# def removeProduct():
# 	form = request.form
# 	res = api.deleteProduct(form)
# 	product = getProduct()

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return render_template("products.html",title=title_+" | Products",user=auth.Adminuser,year=cfg.year(),products=product,product=res)
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/products/category/remove', methods=['POST'])
# def removeCategory():
# 	form = request.form
# 	res = api.deleteCategory(form)
# 	category = getCategory()

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return render_template("product_category.html",title=title_+" | Product Categories",user=auth.Adminuser,year=cfg.year(),categories=category,category=res)
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/products/remove', methods=['POST'])
# def removeUom():
# 	form = request.form
# 	res = api.deleteUom(form)
# 	uom = getUom()

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return render_template("products.html",title=title_+" | Products",user=auth.Adminuser,year=cfg.year(),uoms=product,uom=res)
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/products/type/remove', methods=['POST'])
# def removeType():
# 	form = request.form
# 	res = api.deleteProductType(form)
# 	ptype = getProductType()

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return render_template("products_type.html",title=title_+" | Products Types",user=auth.Adminuser,year=cfg.year(),ptypes=ptype,type=res)
# 	else:
# 		return redirect(url_for("login"))

# @app.route('/products/category', methods=['GET','POST'])
# def Category():  
# 	category = getCategory()
# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return render_template("product_category.html",title=title_+" | Product Categories",user=auth.Adminuser,year=cfg.year(),categories=category)
# 	else:
# 		return redirect(url_for("login"))


# @app.route('/products/category/create', methods=['GET','POST'])
# def addProductCategory():  
# 	form = request.form
# 	res = api.createCategory(form,request.files["image_"]) 
# 	category = getCategory()

# 	if auth.Adminuser["isAuthenticated"] and validateSession(auth.Adminuser): 
# 		return render_template("product_category.html",title=title_+" | Product Categories",user=auth.Adminuser,year=cfg.year(),categories=category,category=res)
# 	else:
# 		return redirect(url_for("login"))



# def validateSession(user):
# 	user_ = cfg.Map(user)
# 	isvalid,session = api.getUserActiveSession(user_)

# 	if isvalid:
# 		return True
# 	else:
# 		return redirect(url_for("login"))
		

# # @app.route('/products/<int:productCode>', methods=['DELETE'])

# # @app.route('/<int:productCode>/product', methods=['PATCH']) 