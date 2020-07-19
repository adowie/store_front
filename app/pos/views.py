from flask import flash, redirect, render_template, url_for,request,session, Markup
from flask_login import login_required, login_user, logout_user,current_user

from . import pos
from ..api import *
from ..func_ import *

title_ = ""

@pos.route('/pos/<int:company>/',methods=["GET","POST"])
@login_required
def pos_(company):
	company_ = Company.query.filter_by(id=company).first()
	session["company"] = company_.as_dict()
	title_ = company_.name
	products = [] 
	error = createPOSSession(company)
	if "success" in error:
		pos_session = error["pos"]
	else:
		flash("Cannot create POS session. Contact admin for assistance","error")
		return redirect(url_for('home.dashboard'))

	categories = getCategoriesByCompany(company_.id)
	products = userItems(current_user,"products",company_.id)
	customer_ = Customer.query.filter_by(customer_type='default').first()
	if pos_session:
		if not pos_session.orders:
			session_ = createNewOrder(pos_session,customer_.id)
		else:
			session_ = pos_session
		return render_template("pos/pos.html",title=title_ +" | POS Session",time=now_time(),user=current_user,categories=categories,products=products,pos=session_)
	else:
		flash("Error starting POS session")
	
	return render_template("home/index.html",title=title_+" | Home",year=year(),company=company_)


@pos.route('/pos/order/create/',methods=["GET","POST"])
@login_required
def new_order():
	company = DDOT(session["company"])
	title_ = company.name
	pos_t = DDOT(request.form.to_dict())
	pos = Pos.query.filter_by(pos_=pos_t.pos_,company_id=pos_t.company_id).first()
	customer_ = Customer.query.filter_by(customer_type='default').first()
	session_ = createNewOrder(pos,customer_.id)
	categories = getCategoriesByCompany(company.id)
	products = userItems(current_user,"products",company.id)
	return render_template("pos/spos.html",title=title_+" | POS Session | Order",user=current_user,time=now_time(),categories=categories,products=products,pos=session_)
	
@pos.route('/pos/order/cancel/',methods=["GET","POST"])
def cancel_order():
	company = DDOT(session["company"])
	title_ = company.name
	order_ = DDOT(request.form.to_dict())
	
	session_ = removeOrder(order_)
	categories = getCategoriesByCompany(company.id)
	products = userItems(current_user,"products",company.id)

	return render_template("pos/spos.html",title=title_+" | POS Session",user=current_user,time=now_time(),categories=categories,products=products,pos=session_)


@pos.route('/pos/order/customer/dialog/',methods=["GET","POST"])
def setCustomersDialog():
	company = DDOT(session["company"])
	title_ = company.name
	pos = DDOT(request.form.to_dict()) 
	customers_ = getCustomersByCompany(pos.company)
	customer = getCustomerbyID(pos.customer)
	
	return render_template("pos/pos_set_customer.html",title=title_+" | POS Session | ",order=pos.order_id,pos=pos.pos_,customers=customers_,customer=customer)
	
@pos.route('/pos/order/products/search/',methods=["GET","POST"])
@login_required
def setProductsDialog():
	pos = DDOT(request.form.to_dict()) 
	products_ = getProductsByName(pos)
		
	return render_template("pos/pos_set_products.html",order=pos.order_id,pos=pos.pos_,products=products_)
	
@pos.route('/pos/order/payment/',methods=["GET","POST"])
@login_required
def setPaymentDialog():
	pos = DDOT(request.form.to_dict()) 
	customers_ = getCustomersByCompany(pos.company)
	customer = getCustomerbyID(pos.customer)
	order = getOrderById(pos)
	company = getCompanyById(pos.company)
	email = company.email if company.email is not None else "[** Set company email go to->setup->company setup tab **]" 
	name = company.name if company.name is not None else "[** Set company name go to->setup->company setup tab **]" 
	logo = company.logo if company.logo is not None else "/img/company/no_logo.png" 
	location = company.location if company.location is not None else "[** Set company location go to->setup->company setup tab **]" 
	contact = company.contact if company.contact is not None else "[** Set company contact go to->setup->company setup tab **]"
	payments = getOrderPayments(pos) 
	foot_note = company.thank_note 
	#"<b>Thank you for your business.</b><br/> Tell us about your experience and suggestions at <br /><b>%s</b>." % email
	head_note = Markup("<span class='company_logo'><img src='/static/%s' alt='Set company logo' /></span><h3>%s</h3> <h5>%s</h5> <h6>%s</h6>" % (logo,name, location , contact))

	return render_template("pos/payment.html",payments=payments,order=order,pos=pos.pos_,customers=customers_,customer=customer,amount_due=pos.amount_due,header=head_note,footer=foot_note)


@pos.route('/pos/order/payment/save/',methods=["GET","POST"])
@login_required
def saveOrderPayment():
	order = DDOT(request.form.to_dict()) 
	payments = addPayment(order)

	return render_template("pos/payments.html",payments=payments)
	

@pos.route('/pos/order/payment/remove/',methods=["GET","POST"])
def removeOrderPayment():
	line = DDOT(request.form.to_dict()) 
	payments = removePayment(line)

	return render_template("pos/payments.html",payments=payments)
	

@pos.route('/pos/order/customer/set/',methods=["GET","POST"])
def setCustomer():
	company = DDOT(session["company"])
	title_ = company.name
	cf = DDOT(request.form.to_dict()) 
	session_ = setPosOrderCustomer(cf)
	categories = getCategoriesByCompany(company.id)
	products = userItems(current_user,"products",company.id)

	return render_template("pos/spos.html",title=title_+" | POS Session",user=current_user,time=now_time(),categories=categories,products=products,pos=session_)
	
@pos.route('/pos/orderline/', methods=["POST"])
def order_line():
	company = DDOT(session["company"])
	title_ = company.name
	item_ = DDOT(request.form.to_dict())	
	orderline = None
	if "add_qty" in item_:
		line_item = OrderLine.query.filter_by(id=item_.line,order_id=item_.order).first()
		line_item_price = getLineItemPrice(line_item)
			
		item = DDOT({"price":float(line_item_price),"qty":float(item_.qty),"discount":line_item.discount})
		orderline = updateOrderLine(line_item,item,company)
	else:
		if "add_discount" in item_:
			line_item = OrderLine.query.filter_by(id=item_.line,order_id=item_.order).first()
			product = Product.query.filter_by(item_code=item_.item_code,company_id=company.id).first()
			line_item_price = getLineItemPrice(line_item)		

			item = DDOT({"price":float(line_item_price),"qty":float(line_item.qty),"discount":item_.discount})
			orderline = updateOrderLine(line_item,item,company)
		else:	
			orderline = createOrderline(item_)
	
	if orderline:
		updateOrder(orderline.order_id)

	products = userItems(current_user,"products",company.id)
	categories = getCategoriesByCompany(company.id)
	session_ = createPOSSession(company.id)

	return render_template("pos/spos.html",title=title_+" | POS Session",user=current_user,time=now_time(),categories=categories,products=products,pos=session_)
	

@pos.route('/pos/orderline/void/', methods=["POST"])
def void_line():
	company = DDOT(session["company"])
	title_ = company.name
	line_ = DDOT(request.form.to_dict())
	orderline_ = orderlineVoid(line_,current_user)
	updateOrder(orderline_.order_id)
	error = createPOSSession(company.id)
	if "success" in error:
		session_ = error["pos"]
	else:
		flash("Cannot create POS session. Contact admin for assistance","error")
		return redirect(url_for('home.dashboard'))
		
	products = userItems(current_user,"products",company.id)
	categories = getCategoriesByCompany(company.id)
	return render_template("pos/spos.html",title=title_+" | POS Session",user=current_user,time=now_time(),categories=categories,products=products,pos=session_)

@pos.route('/pos/orderline/remove/', methods=["POST"])
def remove_line():
	company = DDOT(session["company"])
	title_ = company.name
	line_ = DDOT(request.form.to_dict())
	orderline_ = OrderLine.query.filter_by(id=line_.line,order_id=line_.order).first()
	if orderline_:
		error = db_commit_delete_or_revert(orderline_)
		if not error:
			flash("line item removed successfully.","success");
		updateOrder(line_.order)

	error = createPOSSession(company.id)
	if "success" in error:
		session_ = error["pos"]
	else:
		flash("Cannot create POS session. Contact admin for assistance","error")
		return redirect(url_for('home.dashboard'))
		
	products = userItems(current_user,"products",company.id)
	categories = getCategoriesByCompany(company.id)
	return render_template("pos/spos.html",title=title_+" | POS Session",user=current_user,time=now_time(),categories=categories,products=products,pos=session_)


@pos.route('/pos/close/')
def pos_close():
	title_ = session["company"]["name"]
	return redirect(url_for("osf.land"))
	
	
