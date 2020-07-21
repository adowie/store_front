from flask_login import login_required, login_user, logout_user,current_user

from .func_ import *
from .models import *
from . import db

import sqlalchemy.exc as err
import simplejson as json
import config as conf
import requests
import shutil
import html
import re


def html_to_txt(html_text):
    ## unescape html
    txt = html.unescape(html_text)
    tags = re.findall("<[^>]+>",txt)
  
    for tag in tags:
        txt = txt.replace(tag,'')
    return txt

# determine flash message
def flash_res_msg(res):
	if "error" in res:
		return res["error"],"error"
	else:
		if "success" in res:
			return res["success"],"success"
	return None, None

# start product crud
def db_commit_delete_or_revert(obj):
	db_sess = db.session #open database session
	error = None
	try:
		db_sess.delete(obj) #add prepared statment to opened session
		db_sess.commit()
	except err.SQLAlchemyError as e:
		db_sess.rollback()
		db_sess.flush() # for resetting non-commited .add()
		error = e
	return error 

def db_commit_add_or_revert(obj):
	db_sess = db.session #open database session
	error = None
	try:
		db_sess.add(obj) #add prepared statment to opened session
		db_sess.commit() #commit changes
	except err.SQLAlchemyError as e:
		db_sess.rollback()
		db_sess.flush() # for resetting non-commited .add()
		error = e
	return error


def db_commit_update_or_revert():
	db_sess = db.session #open database session
	error = None
	try:
		db_sess.commit() #commit changes
	except err.SQLAlchemyError as e:
		db_sess.rollback()
		db_sess.flush() # for resetting non-commited .add()
		error = e
	return error

def getItemFromPath(path):
	# Open the url image, set stream to True, this will return the stream content.
	r = requests.get(path, stream = True)
	file_ext = path.split("/")[-1].split(".")[1]
	filename = f'{conf.PRODUCT_IMAGES_DIR}/{str(randomString(11))}.{file_ext}'
	# Check if the image was retrieved successfully
	if r.status_code == 200:
	    # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
	    r.raw.decode_content = True
	    # Open a local file with wb ( write binary ) permission.
	    with open(filename,'wb') as f:
	        shutil.copyfileobj(r.raw, f)
	        
	    return filename
	else:
		return None
	    

def createProduct(form,image):
	if type(form) != dict:
		product = DDOT(form.to_dict())
	else:
		product = DDOT(form)

	error = ""
	if(product.item_code is not None and product.name is not None and product.item_code  and product.name ):

		image_path = save_uploaded_file(image,conf.PRODUCT_IMAGES_DIR)
		product.image = ""
		if image.filename != '':
			product.image = image_path

		product_exist = productExist(product)

		if product_exist:
			# if int(product.update) < 1:
			# 	result = wpos_error_(product_exist_error)
			# else:
			result = updateProduct(product,product.image)
		else:
			product_ = Product(item_code=product.item_code, barcode=barCoder(product.barcode), created_date=convertDateTime(product.created_date), company_id=product.company_id, name=product.name, description=product.description, status=product.status,cost=product.cost, price=product.price, qty=product.qty,taxable=product.taxable, image=product.image)   
			
			error = db_commit_add_or_revert(product_)	
			
			if error:
				result = { "error":error,"form":[product]} #[data] #prepare visual data
			else:
				result = {"product":product_,"success":"Product added successfully."}#prepare visual data

	else:
		result = { "error":"No Product Information to process.","form":[1]}

	return result

def productExist(form):
	product_ = Product.query.filter_by(item_code=form.item_code,company_id=form.company_id).first()
	if product_:
		return True
	return False

def fetchProductsBySearch(search):
	by_ = search.by
	products = []
	searchbycode = []
	error = 0	
	if by_:
		if by_ == "category":
			category_ = Product.query.filter_by(category_id = search.for_).all() #search products by category id
			for prod_ in category_:
				products.append(prod_)
			
			error = products
			
			if len(error) < 1:
				error = {"error":"No Products found in this category"}#if no results return error
				
	else:
		search_product_by_name = Product.query.filter(Product.name.contains(str(search.for_))).all() #search products by name first
		
		searched = search_product_by_name
		if len(search_product_by_name) < 1:
			search_product_by_code = Product.query.filter(Product.item_code.contains(str(search.for_))).all()# on name_search fail search by item code
			searched = search_product_by_code

		if len(searched) < 1:
			error = {"error":"No Products Found"}#if no results return error
		else:
			error = searched
	
	return error

def getProductCategories(product):
	print(product)
	categories = []
	product_categories = CategoryProduct.query.filter_by(product_id=product.id).all()
	for category in product_categories:
		categories.append(category.category_id)
	return categories

def getProductUom(product):
	uom_ = []
	product_uom = UomShedule.query.filter_by(product_id=product.id).all()
	for uom in product_uom:
		uom_.append(uom.uom_id)
	return uom_

def getProducts():  
	data = Product.query.all() #fetch all products on the table
 
	products = []

	for product in data:
		products.append(product)
	 
	return products

def getProductByID(product_code,company):
	product = Product.query.filter_by(item_code=product_code,company_id=company.id).first() #find the product by productId and deletes it
	return product


def deleteProduct(company_id,form):
	del_products = form.getlist("remove_product")
	
	for item_code in del_products:
		Product.query.filter_by(item_code=item_code,company_id=company_id).delete() #find the product by productId and deletes it

		db_sess = db.session #open database session
		db_sess.commit() #commit changes to the database

	return getProducts() #return all create products

def db_commit():
	db_sess = db.session #open database session
	db_sess.commit() #commit changes to the database

def updateProduct(product,image):
	product_ = Product.query.filter_by(item_code=product.item_code,company_id=product.company_id).first()  
	
	error = ""
	prod_ = "product_"
	for k,v in product.items():
		if k != "image":
			exec(prod_+ ".%s = '%s'" % (k,v))# print(prod_+".%s = '%s'" % (k,v))

	if product.image != "":
		product_.image = image
	
	error = db_commit_update_or_revert()

	if error:
		result = { "error":error,"form":[product]} #[data] #prepare visual data
	else:
		result = {"product":product_,"action":"update","success":"Product updated successfully."}#prepare visual data

	return result
# end product crud


# start product category crud
def createCategory(form,image,company):
	if type(form) != dict:
		category = DDOT(form.to_dict())
	else:
		category = DDOT(form)

	error = ""
	if category.name:
		
		image_path = save_uploaded_file(image,conf.PRODUCT_CATEGORY_IMAGES_DIR)

		if image or not category.image:
			category.image = image_path

		category_exist = categoryExist(category,category.name)

		if category_exist:
			result = updateCategory(form,category.image)
		else:
			category_ = Category(name=category.name,parent_id=company.company_type_id,created_date=convertDateTime(category.created_date),image=category.image,active=category.status)   
			error = db_commit_add_or_revert(category_)

			if error:
				result = { "error":error,"form":[category]} #[data] #prepare visual data
			else:
				if company:
					entry = CompanyCategory(company_id=company.id,category_id=category_.id)
					error = db_commit_add_or_revert(entry)
											
				result = {"form":[category_],"success":"Category was added successfully."}#prepare visual data

	else:
		result = { "error":"No Category Information to process.","form":[1]}

	return result

def categoryExist(form,name):
	category = Category.query.filter_by(name=name).first()
	if category:
		return True	
	return False

def getCategories():  
	data = Category.query.all() #fetch all products on the table
	categories = []
	for category in data:
		categories.append(category)
	return categories

def getCategoriesByCompanyType(type_id):
	data = Category.query.filter_by(parent_id=type_id).all() #fetch all products on the table
	categories = []
	for category in data:
		categories.append(category)
	return categories

def getCategoriesByCompany(comp_id):  
	data = CompanyCategory.query.filter_by(company_id=comp_id).all() #fetch all products on the table
	categories = []
	for category in data:
		categories.append(category)
	return categories

def deleteCategory(company, category_id):
	entry = CompanyCategory.query.filter_by(company_id=company.id,category_id=category_id).first() #find the product by productId and deletes it
	category_name = entry.category.name
	error = db_commit_delete_or_revert(entry)
	result = None
	if error:
		result = {"error":"An Unknown error occurred while removing category %s"%category_name}
	else:
		result = {"success":"Category %s was removed from company categories successfully."%category_name}
	return result


def updateCategory(category,image):
	
	image_path = save_uploaded_file(image,conf.PRODUCT_CATEGORY_IMAGES_DIR)
	category_ = Category.filter(name=category.name).first()

	error = ""
	categ_ = "category_"
	for k,v in category.items():
		if k != "image":
			exec(categ_+ ".%s = '%s'" % (k,v))# print(prod_+".%s = '%s'" % (k,v))

	if category.image != "":
		category_.image = image
	
	error = db_commit_update_or_revert()

	if error:
		result = { "error":error,"form":[category]} #[data] #prepare visual data
	else:
		result = {"form":[category_],"action":"update","success":"Product updated successfully."}#prepare visual data

	return result
	# end category crud


# start uom cruddef createCategory(form,image):
	
def createUom(form):
	if type(form) != dict:
		uom = DDOT(form.to_dict())
	else:
		uom = DDOT(form)

	error = ""
	if uom.name and uom.name is not None:
		uom_exist,uom_exist_error = uomExist(uom.name)

		if uom_exist:
			if int(uom.update) < 1:
				result = wpos_error_(uom_exist_error)
			else:
				result = updateUom(uom)
		else:
			uom_ = Uom(name=uom.name,created_date=convertDateTime(uom.created_date),active=uom.status,uom=uom.uom_,conversion=uom.conversion,base=uom.base)   

			db_sess = db.session #open database session
			try:
				db_sess.add(uom_) #add prepared statment to opened session
				db_sess.commit() #commit changes
			except err.SQLAlchemyError as e:
				db_sess.rollback()
				db_sess.flush() # for resetting non-commited .add()
				error = { "error":e,"form":[uom]}

			if error:
				result = error #[data] #prepare visual data
			else:
				result = {"form":[uom]} #prepare visual data
	else:
		result = { "error":"No Unit Of Measure Information to process." }

	return result


def uomExist(name):
	uom = Uom.query.filter_by(name=name).first()
	msg = ""
	if uom is not None:
		msg = {"error":"Unit Of Measure %s already exist" % uom.name}
		return True,msg
	
	return False,0


def getUom():  
	data = Uom.query.all() #fetch all products on the table

	uoms = []

	for uom in data:
		uoms.append(uom)
	 
	return uoms

def deleteUom(form):
	del_uom = form.getlist("remove_uom")
	db_sess = db.session #open database session
	for uom_ in del_uom:
		Uom.query.filter_by(id=uom_).delete() #find the product by productId and deletes it
	db_sess.commit() #commit changes to the database

	return getUom() #return all create products

def deleteVariant(form):
	del_variant = form.getlist("remove_variant")
	db_sess = db.session #open database session
	for variant_ in del_variant:
		Variation.query.filter_by(id=variant_).delete() #find the product by productId and deletes it
	db_sess.commit() #commit changes to the database

def updateVariant(variant,image_):
	variant_ = Variation.query.filter(id=variant.id).first()
	error = ""
	vars_ = "variant_"
	for k,v in variant.items():
		if k != "image":
			exec(vars_+ ".%s = '%s'" % (k,v))# print(prod_+".%s = '%s'" % (k,v))

	if variant.variant_image == "":
		variant_image = request.files["image_"]
		image_path = save_uploaded_file(variant_image, conf.PRODUCT_IMAGES_DIR)
	else: 
		image_path = entry.variant_image
	
	if image_path:
		variant_.image = image_path
	
	error = db_commit_update_or_revert()

	if error:
		result = { "error":error,"form":[variant]} #[data] #prepare visual data
	else:
		result = {"variant":variant_,"action":"update","success":"Product Variant updated successfully."}#prepare visual data
	
	return result
# end uom crud

def updateUom(uom):
	uom_ = Uom.query.filter(name=uom.name).first()

	error = ""
	ums_ = "uom_"
	for k,v in uom.items():
		if k != "image":
			exec(ums_+ ".%s = '%s'" % (k,v))# print(prod_+".%s = '%s'" % (k,v))
	
	error = db_commit_update_or_revert()

	if error:
		result = { "error":error,"form":[uom]} #[data] #prepare visual data
	else:
		result = {"form":[uom_],"action":"update","success":"Unit of Measure updated successfully."}#prepare visual data
	
	return result
# end uom crud


def addProductUoms(product,uom_list):
	error = None
	uoms = []
	for uom in uom_list:
		prod_uom = UomShedule.query.filter_by(product_id=product.id,uom_id=uom).first()
		if not prod_uom:
			product_uom = UomShedule(product_id=product.id,uom_id=uom)
			uoms.append(product_uom)
	
	error = db_insert(uoms)
	return error

def addProductCategories(product,category_list):
	error = None
	categories = []
	for category in category_list:
		prod_category = CategoryProduct.query.filter_by(product_id=product.id,category_id=category).first()
		if not prod_category:
			product_category = CategoryProduct(product_id=product.id,category_id=category)
			categories.append(product_category)
	error = db_insert(categories)
	return error

# start product type crud
def createProductType(form):
	
	product_type = DDOT(form.to_dict())
	error = ""
	if product_type.name and product_type.name is not None:

		product_type_exist,product_type_exist_error = productTypeExist(form,product_type.name)

		if product_type_exist:
			if int(product_type.update) < 1:
				result = wpos_error_(product_type_exist_error)
			else:
				result = updateProductType(form)
		else:
			product_type_ = ProductType(name=product_type.name,created_date=convertDateTime(product_type.created_date) ,active=product_type.status )

			db_sess = db.session #open database session
			try:
				db_sess.add(product_type_) #add prepared statment to opened session
				db_sess.commit()
			except err.SQLAlchemyError as e:
				db_sess.rollback()
				db_sess.flush() # for resetting non-commited .add()
				error = { "error":e,"form":[product_type]}

			if error:
				result = error #[data] #prepare visual data
			else: # for resetting non-commited .add()
				result = {"form":[product_type]} #prepare visual data
	else:
		result = { "error":"No Product Type Information to process.","form":[product_type] }

	return result



def productTypeExist(form,name):
	ptype = ProductType.query.filter_by(name=name).first()
	msg = ""
	if ptype is not None:
		msg = {"error":"Product Type %s already exist. Cannot complete command."%name}
		return True,msg
	
	return False,0

def getProductType():  
	data = ProductType.query.all() #fetch all products on the table

	ptypes = []

	for ptype in data:
		ptypes.append(ptype)
	 
	return ptypes


def deleteProductType(form):
	del_ptype = form.getlist("remove_ptype")
	
	for ptype_name in del_ptype:
		db_sess = db.session #open database session

		ProductType.query.filter_by(name=ptype_name).delete() #find the product by productId and deletes it
		db_sess.commit() #commit changes to the database

	return getProductType() #return all create products


def getCompanyType():  
	data = CompanyType.query.all() #fetch all products on the table

	ctypes = []

	for ctype in data:
		ctypes.append(ctype)
	 
	return ctypes


def deleteCompanyType(form):
	del_ctype= form.getlist("remove_ctype")
	
	for ctype_name in del_ctype:
		db_sess = db.session #open database session

		CompanyType.query.filter_by(name=ctype_name).delete() #find the product by productId and deletes it
		db_sess.commit() #commit changes to the database

	return getCompanyType() #return all create products



def updateCompanyType(form):
	company_type = DDOT(form.to_dict())
	#no use yet

# end company type crud

# start user crud
def createUser(form,image):
	user = DDOT(form)
	error = ""
	result = ""
	image_path = None
	if user.username_ is not None:
		user_exist = userExist(user.email_)
		if user_exist:
			updateUser(form,image)
		else:
			if image:
				image_path = save_uploaded_file(image,conf.USER_IMAGES_DIR)			

			user_ = User(username=user.username_,fullname=user.fullname_,email=user.email_,password=user.password_,image=image_path,created_date=today())   
			db_sess = db.session #open database session
			try:
				db_sess.add(user_) #add prepared statment to opened session
				db_sess.commit() #commit changes
			except err.IntegrityError as e:
				error = e
				db_sess.rollback()
				db_sess.flush() # for resetting non-commited .add()

			# data = User.query.filter_by(id=userId).first() #fetch our inserted product
			if error:
				result = {"error":"An error has been encountered. Please try action again and if error persist contact support."}
			else:
				result = {"success":"You have been successfully registered.<br/>An email with your account information has been sent to the email address you provided.","user":user_}#prepare visual data
				
	else:
		result = {"error":"No User Information to process."}

	return result


def userExist(email):
	user = User.query.filter_by(email=email).first()
	
	if user is not None:
		return True
	
	return False

def getUser():  
	data = User.query.all() #fetch all products on the table

	users = []

	for user in data:
		users.append(user)
	 
	return users


def deleteUser(form):
	del_user = form.getlist("remove_user")
	
	for username in del_user:
		db_sess = db.session #open database session

		User.query.filter_by(username=username).delete() #find the product by productId and deletes it
		db_sess.commit() #commit changes to the database

	return getUser() #return all create products


def updateUser(form):
	user = DDOT(form.to_dict())

	user_ = User.query.filter_by(email=user.email).first()

	# comming soon to a store near you
	
	return result

def make_user_name(name):
	name_arr = name.split(" ")
	user_name = f'{name_arr[0][0]}{name_arr[-1]}'.lower()
	return user_name
# end user crud

# start role crud
def createRole(form):
	role = DDOT(form.to_dict())
	if(role.name is not None):

		role_exist = roleExist(role.name)

		if role_exist:
			updateRole(form)
		else:

			role_ = User(name=role.name,fullname=role.created_date,active=role.active)   

			db_sess = db.session #open database session
			try:
				db_sess.add(role_) #add prepared statment to opened session
				db_sess.commit() #commit changes
			except:
				db_sess.rollback()
				db_sess.flush() # for resetting non-commited .add()
			roleId = role_.id #fetch last inserted id
			data = Role.query.filter_by(id=roleId).first() #fetch our inserted product

			result = [data] #prepare visual data
	else:
		result = { "error":"No Role Information to process." }

	return result


def roleExist(name):
	role = Role.query.filter_by(name=name).first()
	
	if role is not None:
		return True
	
	return False


def getRole():  
	data = Role.query.all() #fetch all products on the table

	roles = []

	for role in data:
		roles.append(role)
	 
	return roles


def deleteRole(form):
	del_role = form.getlist("remove_role")
	
	for name in del_role:
		db_sess = db.session #open database session

		Role.query.filter_by(name=name).delete() #find the product by productId and deletes it
		db_sess.commit() #commit changes to the database

	return getRole() #return all create products

def updateRole(form):
	role = DDOT(form.to_dict())

	#not in use yet
	
	return result
# end role crud
			    


# start oder crud
def createOrder(form):
	order = DDOT(form.to_dict())
	if order.name is not None:
		order_ = Order(name=order.name,user_id=order.user_id,company_id=order.company,order_date=order.date,paid=order.paid,barcode=None,prints=0,session_id=order.session,amount_due=0,sub_total=0,tax_amount=0,disc_amount=0,filter_state="")   
		error = db_commit_add_or_revert(order_)
		if error:
			result = {"error":"Unknown error occurred."}
		else:
			result = [order_] #prepare visual data
	else:
		result = { "error":"No Order Information to process." }

	return result

def orderExist(name):
	order = Order.query.filter_by(name=name).first()
	
	if order is not None:
		return True
	
	return False

def getOrder():  
	data = Order.query.all() #fetch all products on the table

	orders = []

	for order in data:
		orders.append(order)
	 
	return orders


def deleteOrder(form):
	del_order = form.getlist("remove_order")
	
	for name in del_order:
		db_sess = db.session #open database session

		Order.query.filter_by(name=name).delete() #find the product by productId and deletes it
		db_sess.commit() #commit changes to the database

	return getOrder() #return all create products


def updateOrder(order_id):
	result = None
	order_ = Order.query.filter_by(id=order_id).first()
	order_tax = 0
	order_discount = 0
	order_subtotal = 0
	order_total = 0
	if order_:
		for line in order_.orderlines:
			if not line.voided:
				order_tax += float(line.tax)
				order_discount += (line.discount / 100) * float(line.extended)
				order_subtotal += line.extended

		order_.tax_amount = order_tax 
		order_.disc_amount = order_discount 
		order_.sub_total = order_subtotal
		order_.total = float(order_subtotal) + float(order_tax)
		order_.amount_due = float(order_subtotal) + float(order_tax)

		result = db_commit_update_or_revert()

def getOrderById(pos):
	order_ = Order.query.filter_by(id=pos.order,company_id=pos.company,user_id=pos.user,pos_id=pos.pos_id).first()
	return order_

# end order crud

# customer model crud

def createCustomer(form,image): 
	if type(form) == dict:
		customer = DDOT(form)
	else:
		customer = DDOT(form.to_dict())
	error = ""

	if customer.name and customer.name is not None and customer.tax_id and customer.tax_id is not None:

		image_path = save_uploaded_file(image,conf.CUSTOMER_IMAGES_DIR)
		
		if image or not customer.image:
			customer.image = image_path

		customer_exist,customer_exist_error = customerExist(customer)

		if customer_exist:
			if int(customer.update) < 1:
				result = wpos_error_(customer_exist_error)
			else:
				result = updateCustomer(customer,customer.image)
		else:
			customer_ = Customer(name=customer.name,email=customer.email,created_date=customer.created_date,last_business=None,street=customer.street,street2=customer.street2,city=customer.city,zip_code=customer.zip,active=customer.status,customer_type=customer.type,contact=customer.contact,barcode=customer.barcode,credit_limit=None,tax_id=customer.tax_id,avatar=customer.image,company_name=customer.company_name)   

			db_sess = db.session #open database session
			try:
				db_sess.add(customer_) #add prepared statment to opened session
				db_sess.commit() #commit changes
			except err.SQLAlchemyError as e:
				db_sess.rollback()
				db_sess.flush() # for resetting non-commited .add()
				error = { "error":e,"form":[customer]}

			if error:
				result = error #[data] #prepare visual data
			else:
				result = {"customer":customer_,"success":"Customer Account created successfully."} #prepare visual data

	else:
		result = { "error":"No Customer Information to process.","form":[customer]}

	return result


def getCustomersByCompany(company):
	data = Customer.query.filter_by(company_id=company).all()
	customers = []

	for customer in data:
		customers.append(customer)
	 
	return customers


def getCustomerbyID(id_):
	customer = Customer.query.filter_by(id=id_).first()
		 
	return customer

def getCustomerbyEmail(email_):
	customer = Customer.query.filter_by(email=email_).first()
		 
	return customer

def customerExist(form):
	customer = Customer.query.filter_by(email=form.email).first()
	msg = ""

	if customer is not None:
		msg = {"error":"Customer with email %s already exist. You can verify its you by trying to login." % customer.email,"form":[form]}
		return True,msg
	else: 
		return False,0


def deleteCustomer(form):
	del_customer = form.getlist("remove_customer")
	
	for cust_id in del_customer:
		db_sess = db.session #open database session

		Customer.query.filter_by(id=cust_id).delete() #find the customer by id and deletes it
		db_sess.commit() #commit changes to the database

	
	return {"form": [1]}


def getCustomers():  
	data = Customer.query.all() #fetch all customers
	customers = []

	for customer in data:
		customers.append(customer)
	 
	return customers


def updateCustomer(customer,image):
	customer_ = Customer.query.filter_by(email=customer.email).first()  
	cust_ = "customer_"
	error = None

	# print objects
	for k,v in customer.items():
		exec(cust_+ ".%s = '%s'" % (k,v))
	
	if customer.image:
		customer_.avatar = image

	error = db_commit_update_or_revert()
	if error:
		result = {"error":error,"form":[customer]}
	else:
		result = {"customer":customer_,"action":"update","success":"Customer update successful"} #prepare visual data
	
	return result


# crud for company
def createCompany(form,logo,store_front):
	if type(form) != dict:
		company = DDOT(form.to_dict())
	else:
		company = DDOT(form)

	error = ""
	if(company.name is not None):
		company_exist,company_exist_error = companyExist(company,company.name)

		if company_exist:
			if int(company.update) < 1:
				result = wpos_error_(company_exist_error)
			else:
				result = updateCompany(form,logo,store_front)
		else:
			logo_path = save_uploaded_file(logo,conf.COMPANY_IMAGES_DIR)
			store_front_path = save_uploaded_file(store_front,conf.COMPANY_IMAGES_DIR)
			company_ = Company(name=company.name,created_date=company.created_date,email=company.email,logo=logo_path,tax=company.tax,owner_id=company.owner_id,company_type_id=company.type_id,location=company.location,active=company.status,thank_note="Thank you for your business.",contact=company.contact,facebook=company.facebook,instagram=company.instagram,store_front_image=store_front_path,google=company.google,coords=company.coords,twitter=company.twitter,order_hold_limit=company.ohl)   

			db_sess = db.session #open database session
			try:
				db_sess.add(company_) #add prepared statment to opened session
				db_sess.commit() #commit changes
			except err.SQLAlchemyError as e:
				db_sess.rollback()
				db_sess.flush() # for resetting non-commited .add()
				error = { "error":e,"form":[company]}

			if error:
				result = error #[data] #prepare visual data
			else:
				result = {"company":company_,"success":f"Business Account {company.name} successfully create. A confirmation Email has been sent to {company.email}. Verify to complete Sign Up."}#prepare visual data
	else:
		result = { "error":"No Company Information to process.","form":[1] }

	return result


def companyExist(form,name):
	company = Company.query.filter_by(name=name).first()
	
	msg = ""
	if company is not None:
		msg = {"error":"Business Account %s already exist. Cannot complete command"  % company.name,"company":[form]}
		return True,msg
	
	return False,0

def getCompanies():  
	data = Company.query.all() #fetch all companies

	companies = []

	for company in data:
		companies.append(company)
	 
	return companies


def deleteCompany(form):
	del_company = form.getlist("remove_company")
	
	for company_name in del_company:
		db_sess = db.session #open database session

		Company.query.filter_by(name=del_company).delete() #find the company by company name and deletes it
		db_sess.commit() #commit changes to the database

	return getCompany() #return all create company


def getCompanies():  
	data = Company.query.all() #fetch all company on the table

	companies = []

	for company in data:
		companies.append(company)
	 
	return companies

def getCompanyById(comp_id):
	company = Company.query.filter_by(id=comp_id).first()  #fetch all products on the table

	if company is not None:
		return company
	
	return []


def updateCompany(form,logo,store_front):
	company = DDOT(form)
	error = ""
	company_ = Company.query.filter_by(name=company.name).first()  
	
	cust_ = "company_"
	for k,v in company.items():
		exec(cust_+ ".%s = '%s'" % (k,v))# print(prod_+".%s = '%s'" % (k,v))

	if logo:
		company_.logo = save_uploaded_file (logo,conf.COMPANY_IMAGES_DIR)
	if store_front:
		company_.store_front_image = save_uploaded_file (store_front,conf.COMPANY_IMAGES_DIR)

	db_sess = db.session #open database session
	try:
		db_sess.commit() #commit changes
	except err.SQLAlchemyError as e:
		db_sess.rollback()
		db_sess.flush() # for resetting non-commited .add()
		error = {"error":e,"form":[company]}

	if error:
		result = error #[data] #prepare visual data
	else:
		result = {"company":company_,"success":"Company info updated successfully."} #prepare visual data
	
	return result
# end company crud

# crud for company types

def createCompanyType(form):

	ctype = DDOT(form.to_dict())
	error = ""

	if ctype.name and ctype.name is not None:

		ctype_exist,ctype_exist_error = companyTypeExist(ctype)

		# print(image_path)
		# result = {"error":"Test image path","company":[form]}

		if ctype_exist:
			if int(ctype.update) < 1:
				result = wpos_error_(ctype_exist_error)
			else:
				result = updateCompanyType(ctype)
		else:
			companytype_ = CompanyType(name=ctype.name,created_date=ctype.created_date,active=ctype.status)   

			db_sess = db.session #open database session
			try:
				db_sess.add(companytype_) #add prepared statment to opened session
				db_sess.commit() #commit changes
			except err.SQLAlchemyError as e:
				db_sess.rollback()
				db_sess.flush() # for resetting non-commited .add()
				error = { "error":e,"form":[ctype]}

			if error:
				result = error #[data] #prepare visual data
			else:
				result = {"form":[ctype],"error":"success"} #prepare visual data

	else:
		result = { "error":"No company Information to process.","form":[ctype]}

	return result

def companyTypeExist(form):
	companytype = CompanyType.query.filter_by(name=form.name).first()
	msg = ""

	if companytype is not None:
		msg = {"error":"<span class='error'>Company Type %s already exist. Command connot be completed.</span>"  % companytype.name,"form":[form]}
		return True,msg
	else: 
		return False,0


def getCompanyTypes():  
	data = CompanyType.query.all() #fetch all products on the table

	types = []

	for ctype in data:
		types.append(ctype)
	 
	return types


def updateCompanyType(form):
	ctype = form

	companytype_ = CompanyType.query.filter_by(name=ctype.name).first()  
	
	comp_ = "companytype_"
	for k,v in ctype.items():
		exec(comp_+ ".%s = '%s'" % (k,v))# print(prod_+".%s = '%s'" % (k,v))

	db_sess = db.session #open database session
	try:
		db_sess.commit() #commit changes
	except err.SQLAlchemyError as e:
		db_sess.rollback()
		db_sess.flush() # for resetting non-commited .add()
		error = {"error":e,"form":[ctype]}

	if error:
		result = error #[data] #prepare visual data
	else:
		result = {"form":[ctype],"error":"Company type updated successfully"} #prepare visual data
	

	return result


def fetchCustomers(search):
	searching = Customer.query.filter(Customer.name.contains(search)).all()
	
	if searching is None:
		searching = Customer.query.filter(Customer.tax_id.contains(search))
	
	customers = []
	error = ""	
	if searching is None:
		error = {"error":"No Customers Found"}
	else:
		for customer in searching:
			customers.append(customer)

	if len(customers) < 1:
		customers = {"error":"No Customers Found"}

	return customers


def userItems(user,method,filter_):
	items = []
	if method == "products":
		items = Product.query.filter_by(company_id=filter_).all()
		
	if method == "session":
		sessions = user.sessions
		for session in sessions:
			if session.session_ == filter_:
				items = session
	
	return items

def createUserSession(user_id,session_id,company_id):
	if not sessionExist(session_id,company_id):
		new_session = Session(session_=session_id,created_date=today(),active=1,company_id=company_id,user_id=user_id)   
		error = db_commit_add_or_revert(new_session)
		
		if error:
			result = { "error":error,"session":session_id} #error #[data] #prepare visual data
		else:
			result = new_session.session_ #prepare visual data
	

def sessionExist(session_id,company_id):
	session = Session.query.filter_by(session_=str(session_id),company_id=company_id).first()
	if session:
		return True
	return False
		
def getUserActiveSession(user,session_):	
	if len(user.sessions) > 0:
		for session in user.sessions:
			if session.active:
				return session
	return None

def createPOSSession(company):
	pos = Pos.query.filter_by(company_id=company,active=True,created_date=today()).first()
	if not pos:
		pos_id = randomString(16)
		pos_ = Pos(pos_=pos_id,created_date=today(),progress="started",company_id=company)
		error = db_commit_add_or_revert(pos_)
		if error:
			return { "error":error} # error #[data] #prepare visual data
		else:
			pos = pos_
			return {"success": True,"pos":pos} #prepare visual data
	else:
		return {"success": True,"pos":pos}


def getPosActiveSession(user,session):
	pos_session = Pos.query.filter_by(session_id=session.id,user_id=user.id,company_id=session.company_id).first()
	if pos_session:
		return True, pos_session

	return False, None
	

def createNewOrder(pos,customer_id):
	error = ""	
	order_name  = randomString(16)
	order = Order(name=order_name,order_date=now(),paid=None,prints=0,user_id=current_user.id,company_id=pos.company_id,barcode=None,pos_id=pos.id,customer_id=customer_id,amount_due=0,sub_total=0,tax_amount=0,disc_amount=0,filter_state="")

	error = db_commit_add_or_revert(order)
	if error:
		pos_ = { "error":error} #[data] #prepare visual data
	else:		
		pos_ = Pos.query.filter_by(pos_=pos.pos_).first()
		pos_.progress = "inprogress"
		error = db_commit_update_or_revert()

	return pos_ #prepare visual data


def setPosOrderCustomer(cform):
	order = Order.query.filter_by(id=int(cform.order_id),company_id=int(cform.company_id)).first()
	order.customer_id = int(cform.customer_id)

	error = ""
	db_sess = db.session #open database session
	try:
		db_sess.commit()
	except err.SQLAlchemyError as e:
		db_sess.rollback()
		db_sess.flush() # for resetting non-commited .add()
		error = { "error":e}
		print(error)
	
	if not error:
		pos_ = Pos.query.filter_by(pos_=cform.pos_id,company_id=int(cform.company_id)).first()
		return pos_


def removeOrder(order):
	error = ""
	pos_ = Pos.query.filter_by(pos_=order.pos_).first()
	order_ = Order.query.filter_by(id=order.order_id).first()

	if order_ is not None:
		db_sess = db.session #open database session
		
		if order_.orderlines and len(order_.orderlines) > 0:
			for orderline in order_.orderlines:
				db_sess.delete(orderline)
			
			db_sess.delete(order_) #add prepared statment to opened session

		else:
		
			db_sess.delete(order_) #add prepared statment to opened session
		try:
			db_sess.commit()
		except err.SQLAlchemyError as e:
			db_sess.rollback()
			db_sess.flush() # for resetting non-commited .add()
			error = { "error":e}
			
			if error:
				print(error)#for debugging
			
		if error:
			pos_ = error #[data] #prepare visual data
		else:
			pos_ = Pos.query.filter_by(pos_=order.pos_).first()

		if len(pos_.orders) < 1:
			customer_ = Customer.query.filter_by(customer_type='default').first()
			newpos = createNewOrder(pos_,customer_.id)
			pos_ = newpos

	return pos_

def setSessionInactive(user):
	error = ""

	if len(user.session) > 0:
		session = Session.query.filter_by(id=user.session.id).first()

		session.active = 0
		db_sess = db.session #open database session
		try:
			db_sess.commit()
		except err.SQLAlchemyError as e:
			db_sess.rollback()
			db_sess.flush() # for resetting non-commited .add()
			error = e	 
		
		if error:
			print(error)


def createOrderline(item):
	error = ""
	result = ""
	product = Product.query.filter_by(item_code=item.item_code,company_id=item.company_id).first()
	company = Company.query.filter_by(id=item.company_id).first()
	line_item = verifyLineItem(item)
	
	if bool(int(item.cart)):
		result = updateMultiOrderLine(item.items_)
	else:
		if line_item is not None:
			result = updateOrderLine(line_item,item,company)
		else:
			item_tax = 0
			if product.taxable:
				item_tax = (1 * float(product.price)) * (company.tax / 100)
			
			orderline = OrderLine(name=item.name,qty=1,price=product.price,extended=(1 * product.price),tax=item_tax,product_id=product.item_code,discount=0,order_id=int(item.order_id),orderline_date=now(),voided=0)
			error = db_commit_add_or_revert(orderline)
			if error:
				result = error
			else:
				result = orderline

		return result

def updateMultiOrderLine(items_):
	br_items = json.loads(items_)
	result = 0
	for item in br_items:
		itm = DDOT(item)

		line_item = verifyLineItem(itm)
		result = updateOrderLine(line_item,itm)
	else:
		result  = 1

	return result

	# result = OrderLine.query.filter_by(product_id=line_item.product_id,order_id=item.order_id).first()

def verifyLineItem(item):
	line_item = OrderLine.query.filter_by(order_id=int(item.order_id),product_id=item.item_code,name=item.name).first()

	if line_item is not None:
		return line_item
	else:
		return None

def getLineItemPrice(line_item):
	line_item_price = line_item.product.price
	if line_item.name != "base":
		if len(line_item.product.variants) > 0:
			for variant in line_item.product.variants:
				if variant.name == line_item.name:
					line_item_price = variant.price 
	return line_item_price

def updateOrderLine(line_item,item,company):
	error = ""
	result = ""
	item_price = float(item.price)
	if item.discount:
		item_discount = (float(item.discount) / 100) * float(item.price)
		item_price = float(float(item.price) - float(item_discount))

	if line_item.tax:
		item_tax = (float(item.qty) * float(item_price)) * (float(company.tax) / 100)
	
	extended = float(item.qty) * item_price
	line_item.qty = item.qty
	line_item.tax = item_tax
	line_item.price = item_price
	line_item.extended = extended
	line_item.discount = item.discount
	line_item.underline_date = now()

	error = db_commit_update_or_revert()
	if error:
		result = error
	else:
		result = line_item#OrderLine.query.filter_by(product_id=line_item.product_id,order_id=item.order_id).first()
	return result


def orderlineVoid(line,user):
	orderline = OrderLine.query.filter_by(id=int(line.line),order_id=line.order).first()
	# sess,result = getPosActiveSession(user)
	error = None
	result = None
	if orderline:
		if orderline.voided:
			orderline.voided = 0
		else:
			orderline.voided = 1

		error = db_commit_update_or_revert()
		if error:
			result = error
			print(error)
		else:
			result = orderline

	return result


# payments
def addPayment(order):
	error = ""
	payments = []
	payment = Payment(pos_id=order.pos_,name=order.payment_id,amount_due=float(order.amount_due),amount_tended=float(order.amount_received),voided=0,created_date=convertDateTime(now()),order_id=order.order,payment_type_id=order.payment_method,change=float(order.change))

	db_sess = db.session #open database session

	try:
		db_sess.add(payment)
		db_sess.commit()
	except err.SQLAlchemyError as e:
		db_sess.rollback()
		db_sess.flush() # for resetting non-commited .add()
		error = {"error":e}

	if error:
		print(error)
	else:
		payments = getOrderPayments(order)

	return payments


def removePayment(line):
	error = ""
	payments = []
	payment = Payment.query.filter_by(pos_id=line.pos_,name=line.payment,order_id=line.order)

	db_sess = db.session

	if payment:
		payment.delete()
		db_sess.commit()

	return payments

def getOrderPayments(order):
	data = Payment.query.filter_by(order_id=order.order,pos_id=order.pos_).order_by(Payment.amount_due.desc()).all()
	payments = []

	if data is not None:
		for payment in data:
			payments.append(payment)

	return payments


	





