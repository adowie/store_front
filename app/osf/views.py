from flask import flash, redirect, render_template, url_for,request,session,Markup, abort
from flask_login import login_required, login_user, logout_user,current_user
from flask_paginate import Pagination, get_page_args

from . import osf
from .. import db
from sqlalchemy import extract
from ..api import *
from ..models import *
from ..func_ import *
from bson import json_util
import simplejson as json
import geocoder



@osf.route('/',methods=['GET', 'POST'])
def land():
	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]

	bus_types = CompanyType.query.all()
	return render_template("osf/index.html",title="Home",bus_types=bus_types,is_admin=is_admin)


@osf.route('/vline/status/<int:business>/<int:status>/', methods=['GET', 'POST'])
@login_required
def vlinestatus(business,status):
	company_ = Company.query.filter_by(id=business).first()
	if status == 1:
		flash("Appointment was flagged as Honoured.")
	else:
		if status == 2:
			flash("Appointment was flagged as Not Honoured.")

	return redirect(url_for('osf.companies',company_type=company_.company_type_id))


@osf.route('/vline/<int:business>/', methods=['GET', 'POST'])
@login_required
def vline(business):
	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]

	customer_ = Customer.query.filter_by(email=current_user.email).first()
	joined = ""
	if customer_:
		rejoin = False
		place_in_line = 0
		company_ = Company.query.filter_by(id=business).first()
		vline_ = Vline.query.filter_by(company_id=business,created_date=today()).first()

		if vline_:
			vlineup_ = Vlineup.query.filter_by(company_id=business,user_id=current_user.id,line_id=vline_.id).first()
			if vlineup_:
				rejoin = True
				joined = vlineup_.joined
			
			if vline_.serving != -1:
				place_in_line = len(vline_.lineup)

				if vlineup_:
					rejoin = True
					joined = vlineup_.joined
					place_in_line = vlineup_.place_in_line

			else:
				flash("This virtual line is closed.")
				return redirect(url_for('osf.companies',company_type=company_.company_type_id))
		else:
			flash(f"{company_.name} has no active virtual lines for today.")
			return redirect(url_for('osf.companies',company_type=company_.company_type_id))
	else:
		flash("You need a customer account to access that resource.")
		return redirect(url_for('osf.account'))
	

	return render_template("osf/vline.html",title="Virtual Line",company=company_,rejoin=rejoin,place_in_line=place_in_line,line=vline_,joined=joined,is_admin=is_admin)

@osf.route('/vline/join/<int:business>/', methods=['GET', 'POST'])
@login_required
def joinvline(business):

	customer_ = Customer.query.filter_by(email=current_user.email).first()
	if customer_:
		rejoin = True
		place_in_line = 0
		company_ = Company.query.filter_by(id=business).first()
		vline_ = Vline.query.filter_by(company_id=business,created_date=today()).first()
		if vline_:
			if vline_.serving != -1:
				inline_ = Vlineup.query.filter_by(line_id=vline_.id,company_id=business,user_id=current_user.id).first()
				if not inline_:
					place_in_line = len(vline_.lineup) + 1
					vlineup_ = Vlineup(line_id=vline_.id,company_id=business,user_id=current_user.id,joined=now(),place_in_line=place_in_line)
					error = db_commit_add_or_revert(vlineup_)
					if not error:
						flash("Your place in line has been secured.","success")
						rejoin = False
					else:
						flash("There was an error placing you in line. You may try again or contact admin if the problem persists.","error")
				else:
					rejoin = True
					place_in_line = inline_.place_in_line
					flash("You are already in this line","success")

			else:
				flash("This Virtual line is closed")
				return redirect(url_for('osf.companies',company_type=company_.company_type_id))
		else:
			flash(f'{company_.name} has no active virtual lines.')
	else:
		flash("You need a customer account to access that resource.")
		return redirect(url_for('osf.account'))
	return redirect(url_for('osf.vline',business=business))
	

@osf.route('/about/', methods=['GET', 'POST'])
def about():

	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]
	return render_template("osf/about.html",title="About",is_admin=is_admin)

@osf.route('/contact/', methods=['GET', 'POST'])
def contact():

	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]
	return render_template("osf/contact.html",title="Contact",is_admin=is_admin)

@osf.route('/companies/<int:company_type>/', methods=['GET', 'POST'])
def companies(company_type):

	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]

	fav_companies = []
	business_of_type = Company.query.filter_by(company_type_id=company_type,published=1).all()
	if current_user.is_authenticated:
		customer_ = Customer.query.filter_by(email=current_user.email).first()
		companies_ = FavouriteCompany.query.filter_by(customer_id=customer_.id).all()

		for company in companies_:
			fav_companies.append(company.company_id)
	if len(business_of_type) < 1:
		return redirect(url_for('osf.land'))
	return render_template("osf/companies.html",title="Companies",resgistered_businesses=business_of_type,is_admin=is_admin,fav_companies=fav_companies)

@osf.route('/account/',defaults={"account_type":None}, methods=['GET', 'POST'])
@osf.route('/account/<account_type>/', methods=['GET', 'POST'])
def account(account_type):
	is_admin = False
	comp_types = getCompanyType()
	form = request.form
	activation_link = None
	if "account_type" in form: 
		if int(form["account_type"]) == 3:
			user = User.query.filter_by(email=form["bus_email"]).first()
			if not user:
				new_user = {"username_":make_user_name(form["bus_owner"]),"fullname_":form["bus_owner"],"email_":form["bus_email"],"password_":form["bus_pass"]}
				res = createUser(new_user,request.files["image_"]) 
				if "success" in res:
					user_ = res["user"]
					owner_id = user_.id
			else:
				owner_id = user.id

			location = f'{form["bus_address"]},{form["bus_state"]},{form["bus_city"]},{form["bus_postal"]}'
			company = {"name":form["bus_name"],"created_date":today(),"contact":form["bus_phone"],"email":form["bus_email"],"tax":form["bus_tax"],"owner_id":owner_id,"type_id":form["bus_type"],"location":location,"status":0,"update":0}#account to be verified b4 it becomes active

			res = createCompany(company,request.files["image_"],request.files["store_front_image"])
			if "success" in res:
				# add business as customer by default
				customer_ = Customer(name=form["bus_owner"],email=form["bus_email"],created_date=now(),last_business=None,street=form["bus_address"],street2={form["bus_state"]},city=form["bus_city"],zip_code=form["bus_postal"],active=1,customer_type="normal",contact=form["bus_phone"],barcode="",credit_limit=None,tax_id="000000000",avatar="img/customers/default.png",company_name=form["bus_name"])   
				error = db_commit_add_or_revert(customer_)
				token = company_.get_activation_token()
				params = {"type":"company","name":company_.owner.fullname,"app_link":url_for('osf.land',_external=True),"rec_link":url_for('osf.activate',token=token,_external=True),"email":company_.email,"contact":Markup(f'Email: {conf.COMPANY_EMAIL}<br>Mobile: {conf.COMPANY_MOBILE}<br>Telephone: {conf.COMPANY_TELEPHONE}<br><span style="font-size:12px;">You can also reach out to us using the contact us form on the portal.</span><br>')}
				user_.add_notification("activation", "company", user_.id, "Company Account Activation", json.dumps(params, default=json_util.default), 0)


			msg, msg_type = flash_res_msg(res)
			if msg:
				flash(msg,msg_type)

			company_ = Company.query.filter_by(email=form["bus_email"]).first()
			if not company_.active:
				activation_link = Markup(f"<a class='btn btn-success' id='activation_link' href='{url_for('osf.resend',account_type=2,email=company_.email)}'>Resend Activation link</a>")
			else:
				flash("Your Business Account is already active. You may need to use account recovery to regain access.")
		else:
			if int(form["account_type"]) == 2:
				user = User.query.filter_by(email=form["cus_email"]).first()
				cus_full_name = f'{form["cus_fname"]} {form["cus_lname"]}'

				if not user:
					new_user = {"username_":make_user_name(cus_full_name),"fullname_":cus_full_name,"email_":form["cus_email"],"password_":form["cus_pass"]}
					res = createUser(new_user,request.files["image_"]) 

					if "success" in res:
						user_ = res["user"]
						user_id = user_.id
				else:
					user_id = user.id

				if user_id:
					customer = {"name":cus_full_name,"email":form["cus_email"],"created_date":today(),"street":"","street2":"","city":"","zip":"","status":0,"type":"normal","contact":form["cus_phone"],"tax_id":"000000000","image":"img/customers/default.png","company_id":"","company_name":"","barcode":"","update":0}
					res = createCustomer(customer,request.files["image_"])	
						
					if "success" in res:
						customer_ = res["customer"]
					
						token = customer_.get_activation_token()
						params = {"type":"customer","name":customer_.name,"app_link":url_for('osf.land',_external=True),"rec_link":url_for('osf.activate',token=token,_external=True),"email":customer_.email,"contact":Markup(f'Email: {conf.COMPANY_EMAIL}<br>Mobile: {conf.COMPANY_MOBILE}<br>Telephone: {conf.COMPANY_TELEPHONE}<br><span style="font-size:12px;">You can also reach out to us using the contact us form on the portal.</span><br>')}
						user_.add_notification("activation", "customer", user_.id, "Customer Account Activation", json.dumps(params, default=json_util.default), 0)
						

					msg, msg_type = flash_res_msg(res)
					if msg:
						flash(msg,msg_type)
					
					customer_ = Customer.query.filter_by(email=form["cus_email"]).first()
					if not customer_.active:
						activation_link = Markup(f"<a id='resend' class='btn btn-success' id='activation_link' href='{url_for('osf.resend',account_type=1,email=customer_.email)}'>Resend Activation link</a>")
					else:
						flash("Your Customer Account is already active. You may need to use account recovery to regain access.")
			else:
				if int(form["account_type"]) == 1:
					user_ = User.query.filter_by(email=form["log_email"]).first()
					if user_:
						# print(form["log_pass"])
						if user_.verify_password(form["log_pass"]):
							login_user(user_)
							session_id = randomString(16)
							accounts = []
							business_ = Company.query.filter_by(email=form["log_email"],active=1).first()
							customer_ = Customer.query.filter_by(email=form["log_email"],active=1).first()
							if business_:
								accounts.append({"type":2,"account":business_})
								session["company"] = business_.as_dict()
								session["is_admin"] = True

							if customer_:
								accounts.append({"type":1,"account":customer_})

							session["id"] = session_id

							if len(accounts) < 1:
								flash("The Account you registered is not yet activated. Check your email for activation link.")
							else:									
								return redirect(url_for('osf.land'))
							# else:
							# 	return render_template("osf/accounts.html",title="Proceed as",cus_accounts=accounts)
						else:
							flash("Invalid Credentials","error")
					else:
						flash(f"No account found for {form['log_email']}. Create an account to proceed.","error")

	return render_template("osf/account.html",title="Sign In | Sign Up",form=form,account_type=account_type,company_types=comp_types,activation_link=activation_link,is_admin=is_admin)


@osf.route('/account/activation/<int:account_type>/<email>/', methods=['GET', 'POST'])
def resend(account_type,email):
	if account_type == 2:
		company_ = Company.query.filter_by(email=email).first()
		user_ = User.query.filter_by(email=email).first()
		# mail_send_res = accountVerification(company_,"company")
		if user_:
			token = company_.get_activation_token()
			params = {"type":"company","name":company_.owner.fullname,"app_link":url_for('osf.land',_external=True),"rec_link":url_for('osf.activate',token=token,_external=True),"email":company_.email,"contact":Markup(f'Email: {conf.COMPANY_EMAIL}<br>Mobile: {conf.COMPANY_MOBILE}<br>Telephone: {conf.COMPANY_TELEPHONE}<br><span style="font-size:12px;">You can also reach out to us using the contact us form on the portal.</span><br>')}
			user_.add_notification("activation", "company", user_.id, "Company Account Activation", json.dumps(params, default=json_util.default), 0)

	else:
		if account_type == 1:
			customer_ = Customer.query.filter_by(email=email).first()
			# mail_send_res = accountVerification(customer_,"customer")
			user_ = User.query.filter_by(email=email).first()
			# mail_send_res = accountVerification(company_,"company")
			if user_:
				token = customer_.get_activation_token()
				params = {"type":"customer","name":customer_.name,"app_link":url_for('osf.land',_external=True),"rec_link":url_for('osf.activate',token=token,_external=True),"email":email,"contact":Markup(f'Email: {conf.COMPANY_EMAIL}<br>Mobile: {conf.COMPANY_MOBILE}<br>Telephone: {conf.COMPANY_TELEPHONE}<br><span style="font-size:12px;">You can also reach out to us using the contact us form on the portal.</span><br>')}
				user_.add_notification("activation", "customer", user_.id, "Customer Account Activation", json.dumps(params, default=json_util.default), 0)
			
	flash("You should receive an activation link within the next 5 minutes, otherwise contact us at support@ourstorefront.online","success")
	return redirect(url_for('osf.account'))

@osf.route('/account/activate/', defaults={'token':None}, methods=['GET', 'POST'] )
@osf.route('/account/activate/<token>/', methods=['GET', 'POST'])
def activate(token):
	if token:
		company = Company.verify_activation_token(token)
		if company:
			company.active = 1
			db_commit()
			flash('Your account has been successfully activated. You can now login.','success')
		else:
			customer = Customer.verify_activation_token(token)
			if customer:
				customer.active = 1
				db_commit()
				flash('Your account has been successfully activated. You can now login.','success')
			else:
				flash('Invalid Token','error')
						

	form = {"account_type": 1}
	return render_template('osf/account.html', form=form)

@osf.route('/account/recover/', defaults={'token':None}, methods=['GET', 'POST'] )
@osf.route('/account/recover/<token>', methods=['GET', 'POST'])
def recover(token):
	is_admin = False
	form = request.form
	res = None
	if form:
		if token:
			res_ = resetUserPassword(form["password"],token)
			if 'success' in res_:
				flash('Your account has been successfully recovered. You can now login.',"success")
				return redirect(url_for('osf.account'))
			else:
				if "token" in res_:
					flash(res_["token"],"error")
					return redirect(url_for('osf.account'))
		else:
			if "email" in form:
				user_ = User.query.filter_by(email=form["email"]).first()
				if user_:
					if user_.customer and user_.customer.active or user_.company and user_.company.active:
						token = user_.get_recover_password_token()
						params = {"type":"customer","name":customer_.name,"app_link":url_for('osf.account',_external=True),"rec_link":url_for('osf.recover',token=token,_external=True),"email":user_.email,"contact":Markup(f'Email: {conf.COMPANY_EMAIL}<br>Mobile: {conf.COMPANY_MOBILE}<br>Telephone: {conf.COMPANY_TELEPHONE}<br><span style="font-size:12px;">You can also reach out to us using the contact us form on the portal.</span><br>')}
						user_.add_notification("recovery", "osf", user_.id, "Customer Account Recovery",json.dumps(params, default=json_util.default), 0)
						flash("A recovery email has been sent to email provided. Check your email for instructions to recover your account","success")

						return redirect(url_for('osf.account'))
					else:
						flash(f"The account associated with email {user_.email} is not active. Log in to {user_.email} and follow account activation instructions.","error")
				else:
					flash(Markup(f"No OSFO account found with email {form['email']}. Register new account <a href='{url_for('osf.account',account_type=3)}'> here</a>"),"error")

	return render_template('osf/recover.html', form=form,token=token,title="Recover Account",is_admin=is_admin)


@osf.route('/shop/<int:company>/',defaults={'category':0}, methods=['GET', 'POST'])
@osf.route('/shop/<int:company>/<int:category>/', methods=['GET', 'POST'])
@login_required
def shop(company,category):
	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]

	company_ = Company.query.filter_by(id=company).first()
	page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
	if per_page == 10:
		per_page = 12
		
	if category:
		# category_ = CompanyCategory.query.filter_by(category_id=category,company_id=company).first();
		products = []
		products_all = Product.query.filter_by(company_id=company,status=True).all()
		for product in products_all:
			if category in product.categories:
				products.append(product)	
		page_products = products[offset: offset + per_page]
	else:
		products = Product.query.filter_by(company_id=company,status=True).all()
		page_products = products[offset: offset + per_page]

	pagination = Pagination(page=page, per_page=per_page, offset=offset,total=len(products))

	pos_ = Pos.query.filter_by(company_id=company,active=True).first()
	customer = Customer.query.filter_by(email=current_user.email).first()

	if company_.closed:
		flash("Company is closed, no orders will be processed at this time.")
		return redirect(url_for('osf.companies',company_type=company_.company_type_id))

	if customer:
		active_order = Order.query.filter_by(user_id=current_user.id,company_id=company,status=0,customer_id=customer.id).first()

		if not active_order:
			if pos_:
				active_order = Order(name=randomString(16),pos_id=pos_.id,user_id=current_user.id,company_id=company,order_date=now(),status=0,customer_id=customer.id)
				error = db_commit_add_or_revert(active_order)
			else:
				flash("It seems company is not accepting orders at this time.")
				return redirect(url_for('osf.companies',company_type=company_.company_type_id))
	else:
		flash("You need a customer account to access that resource.")
		return redirect(url_for('osf.account'))

	fav_products = []
	for product in customer.fav_products:
		fav_products.append(product.product_id)


	return render_template("osf/shop.html",title="Shop",company=company_,is_admin=is_admin,products=page_products,page=page,
                           per_page=per_page,total=len(products),pagination=pagination,in_category=category,active_order=active_order,fav_products=fav_products)


@osf.route('/shop/order/<int:company>/<int:category>/<int:customer>/<int:item>/<item_name>/', methods=['GET', 'POST'])
@login_required
def add_osf_order(company,category,item,customer,item_name):
	company_ = Company.query.filter_by(id=company).first()
	if company_:
		pos_ = Pos.query.filter_by(company_id=company,active=True).first()
		product = Product.query.filter_by(id=item,company_id=company).first()
		if item_name == "base":
			product_price = product.price
		else:
			for variant in product.variants:
				if variant.name.lower() == item_name.lower():
					product_price = variant.price
					
		error = None
		if pos_:
			customer_active_order = Order.query.filter_by(user_id=current_user.id,company_id=company,status=0,customer_id=customer).first()
			if not customer_active_order:
				customer_active_order = Order(name=randomString(16),pos_id=pos_.id,user_id=current_user.id,company_id=company,order_date=now(),status=0,customer_id=customer)
				error = db_commit_add_or_revert(customer_active_order)
			
			if not error:
				orderline_ = OrderLine.query.filter_by(product_id=product.item_code,order_id=customer_active_order.id,name=item_name).first()				
				if not orderline_:
					item_tax = 0
					if product.taxable:
						item_tax = (1 * float(product_price)) * (company_.tax / 100)
					
					orderline_ = OrderLine(name=item_name,qty=1,price=product_price,extended=((1 * float(product_price))),tax=item_tax,product_id=product.item_code,discount=0,order_id=customer_active_order.id,orderline_date=now(),voided=0)
					error = db_commit_add_or_revert(orderline_)
					if error:
						flash("Unable to add item to order.")
					else:
						flash("Item added to order.")
				else:
					item_tax = 0
					new_qty = orderline_.qty + 1
					orderline_.qty = new_qty
					orderline_.price = product_price
					if product.taxable:
						item_tax = (new_qty * float(product_price)) * (company_.tax / 100)
					
					orderline_.extended = new_qty * float(product_price) 
					orderline_.tax = item_tax
					error = db_commit_update_or_revert()
					if not error:
						flash("Order updated.")
				if orderline_:
					updateOrder(orderline_.order_id)
			else: 
				flash(f"error: {error}")

		else:
			flash("It seems company is not accepting orders at this time.")

		return redirect(url_for('osf.shop',company=company,category=category))
	return redirect(url_for('osf.account'))


@osf.route('/orders/', methods=['GET', 'POST'])
@login_required
def orders():
	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]

	customer = Customer.query.filter_by(email=current_user.email).first()
	orders = customer.orders

	return render_template("osf/orders.html",title="Orders",is_admin=is_admin,orders=orders)

@osf.route('/order/<int:order>/<int:customer>/<int:company>/', methods=['GET', 'POST'])
@login_required
def order(order,customer,company):
	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]
	order = Order.query.filter_by(id=order,customer_id=customer,company_id=company).first()

	if len(order.orderlines) < 1:
		return redirect(url_for('osf.shop',company=company))

	return render_template("osf/cart.html",title="Orders",is_admin=is_admin,order=order)


@osf.route('/order/line/remove/<int:company>/<int:order>/<int:line>/<int:customer>/', methods=['GET', 'POST'])
@login_required
def remove_orderline(company,line,order,customer):
	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]

	order_ = Order.query.filter_by(id=order,customer_id=customer,company_id=company).first()
	if order_:
		orderline_ = OrderLine.query.filter_by(id=line,order_id=order).first()
		error = db_commit_delete_or_revert(orderline_)
		if error:
			flash("Unable to remove line from order.")
		else:
			updateOrder(order)

	if len(order_.orderlines) < 1:
		return redirect(url_for('osf.shop',company=company))
	return redirect(url_for('osf.order',order=order,company=company,customer=customer))
	

@osf.route('/order/send/<int:order>/<int:customer>/<int:company>/', methods=['GET', 'POST'])
@login_required
def sendorder(order,customer,company):
	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]
	
	order = Order.query.filter_by(id=order,customer_id=customer,company_id=company).first()
	if not order.company.closed:
		mail_send_res = sendOrderConfirmation(order,"confirmed")
		if "success" in mail_send_res:
			order.filter_state = "sent"
			error = db_commit_update_or_revert()
			if not error:
				flash(f"Order has been sent to {order.company.name}. Please await fulfillment verification.")
	else:
		flash(f"{order.company.name} is not processing any orders at the moment. Company closed.")

	return render_template("osf/order_confirmation.html",title="Orders",is_admin=is_admin,order=order)

@osf.route('/company/detail/<name>/<int:_id>/', methods=['GET', 'POST'])
def company(name,_id):
	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]
	company = Company.query.filter_by(id=_id,name=name).first()
	geo = {}
	if company:
		if not company.coords:
			address = ",".join(company.location.split(',')[:-1])
			geo = geocoder.osm(f'{ address }')
			if not geo:
				geo["json"] = {"raw":{"lat":18.47369,"lon":-77.92209},"zoom": 11}
			else:
				geo.json["zoom"] = 25
				print(geo.json)
				company.coords = f'{geo.json["raw"]["lat"]},{geo.json["raw"]["lon"]}'
				error = db_commit_update_or_revert()
				if error:
					print(error)
		else:
			print(company.coords)
			geo["json"] = {"raw":{"lat":0,"lon":0,"zoom":25}}#{"raw":{"lat":company.coords.split(",")[0],"lon":company.coords.split(",")[1]},"zoom":25}
	else:
		abort(404)
	return render_template("osf/company_detail.html",title=f"Detail | {company.name}",is_admin=is_admin,company=company,geo=geo["json"])

@osf.route('/favourite/', methods=['GET', 'POST'])
@login_required
def favs():
	form = DDOT(request.form)
	customer_ = Customer.query.filter_by(email=current_user.email).first()
	customer = customer_.id
	company = int(form.company)
	fav_type = int(form.type)
	fav_id = int(form.item)
	error = None
	command = 0
	if customer_:
		if fav_type == 1:
			company = Company.query.filter_by(id=fav_id).first()
			if company:
				fav_company = FavouriteCompany.query.filter_by(company_id=fav_id,customer_id=customer).first()
				if not fav_company:
					fav_company = FavouriteCompany(company_id=fav_id,customer_id=customer)
					error = db_commit_add_or_revert(fav_company)
				else:
					command = 1
					error = db_commit_delete_or_revert(fav_company)
		else:
			if fav_type == 2:
				fav_product = FavouriteProduct.query.filter_by(company_id=company,product_id=fav_id,customer_id=customer).first()
				if fav_product:
					command = 1
					error = db_commit_delete_or_revert(fav_product)
				else:
					fav_product = FavouriteProduct(company_id=company,customer_id=customer,product_id=fav_id)
					error = db_commit_add_or_revert(fav_product)
	
	favs_ = 0
	fav_comps = FavouriteCompany.query.filter_by(customer_id=customer).all()
	fav_prods = FavouriteProduct.query.filter_by(customer_id=customer).all()
	favs_ = len(fav_comps) + len(fav_prods)
	if not error:
		error = {"success":1,"favs": favs_,"command":command}
	else:
		error = {"success":0,"favs": favs_}

	return json.dumps(error)

@osf.route('/favourites/', methods=['GET', 'POST'])
@login_required
def favourites():
	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]

	customer_ = Customer.query.filter_by(email=current_user.email).first()
	favs = {"companies":customer_.fav_companies,"products":customer_.fav_products}

	return render_template("osf/favourites.html",title=f"Favourites",is_admin=is_admin,favourites_=favs)

@osf.route('/osf/search/', methods=['GET', 'POST'])
def search():
	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]

	form = DDOT(request.form)
	search = form.search
	search_type = int(form.search_type)
	
	fav_companies = []
	fav_products = []
	customer_id = 0
	if current_user.is_authenticated:
		customer_ = Customer.query.filter_by(email=current_user.email).first()
		customer_id = customer_.id
		for company in customer_.fav_companies:
			fav_companies.append(company.company_id)
		for product in customer_.fav_products:
			fav_products.append(product.product_id) 

	search_ = {}
	if search_type == 1 and search:
		results = Company.query.filter(Company.name.contains(search)).all()
		if results:
			search_["companies"] = results
	else:
		if search_type == 2 and search:
			results = Product.query.filter(Product.name.contains(search)).all()
			if results:
				search_["products"] = results

	return render_template("osf/search_results.html",title=f"Search Results",is_admin=is_admin,search_=search_,fav_companies=fav_companies,fav_products=fav_products, search=search,customer_id=customer_id,search_by=search_type)


@osf.route('/subscribe/', methods=['GET', 'POST'])
def subscribe():
	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]

	form = DDOT(request.form)
	subscriber = Subscriber.query.filter_by(email=form.email).first()
	if not subscriber:
		subscriber = Subscriber(email=form.email,created_date=now())
		error = db_commit_add_or_revert(subscriber)
		
	return render_template("osf/subscriber.html",title=f"Subscriber",is_admin=is_admin)


@osf.route('/unsubscribe/<email>/', methods=['GET', 'POST'])
def unsubscribe(email):
	is_admin = False
	if "is_admin" in session:
		is_admin = session["is_admin"]

	subscriber = Subscriber.query.filter_by(email=email).first()
	if subscriber:
		error = db_commit_delete_or_revert(subscriber)
				
	return render_template("osf/unsubscriber.html",title=f"Unsubscriber",is_admin=is_admin)


@osf.route('/logout/', methods=['GET', 'POST'])
def logout():
	if "is_admin" in session:
		session.pop('is_admin')
	
	logout_user()
	flash('You have been successfully logged out.')
	return redirect(url_for('osf.land'))

