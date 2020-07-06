from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import time
from app import db, login_manager
import config as conf
import os
import json

# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String

# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Access(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	user = db.relationship('User',back_populates="access",foreign_keys=user_id)

	view_id = db.Column(db.Integer, db.ForeignKey('view.id'))
	view = db.relationship("View")

	def __repr__(self):
		return '<Access %s,%s,%s>' % (self.user_id,self.view_id)


class View(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(60), unique=True)
	is_active = db.Column(db.Boolean, default=True)

	def __repr__(self):
		return '<View %s>' % (self.name)


class User(UserMixin,db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), index=True)
	fullname = db.Column(db.String(64), index=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_ = db.Column(db.String(220), index=True)
	created_date = db.Column(db.DateTime)
	image = db.Column(db.String(224), default='img/user/default.png')
	last_login = db.Column(db.DateTime)
	is_logged_in = db.Column(db.Boolean, default=False)
	is_admin = db.Column(db.Boolean, default=False)

	notifications = db.relationship('Notification', backref='users',lazy='dynamic')
	access = db.relationship('Access',back_populates="user")
	company = db.relationship('Company',back_populates="owner")
	sessions = db.relationship('Session',back_populates="user")
	orders = db.relationship('Order',back_populates="user")
	customer = db.relationship('Customer',back_populates="user")
	lineup = db.relationship('Vlineup',back_populates="user")

	@property
	def password(self):
		"""
		Prevent password from being accessed
		"""
		return self.password_

	# return self._password
	@password.setter
	def password(self, value):
		"""
		Set password to a hashed password
		"""
		self.password_ = generate_password_hash(value)


	def verify_password(self, password_):
		"""
		Check if hashed password matches actual password
		"""
		return check_password_hash(self.password_, password_)
	
	def get_recover_password_token(self, expires_in=600):
		return jwt.encode({'recover_password': self.id, 'exp': time.time() + expires_in},conf.SECRET_KEY, algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_recover_password_token(token):
		try:
			id = jwt.decode(token, conf.SECRET_KEY, algorithms=['HS256'])['recover_password']
		except:
			return
		return User.query.get(id)
	
	def add_notification(self, name, type_, user, data, params, sent):
		notif_ = Notification.query.filter_by(type_=type_, name=name, user_id=user).first()
		
		if notif_:
			notif_.params = params
			notif_.sent = 0
		else:	
			notif = Notification(type_=type_, name=name, message=data, params=params, user_id=user, sent=sent)
			db.session.add(notif)
		
		db.session.commit()

	def update_last_login(self):
		self.last_login = time.strftime("%Y-%m-%d %H:%M:%S")

	def update_is_logged_in(self, state):
		self.is_logged_in = state
	
	def update_notification_sent_flag(self, notif_id,flag):
		notif_ = Notification.query.filter_by(id=notif_id).first()
		notif_.sent = flag
		db.session.commit()

	def __repr__(self):
		return '<User %s,%s,%s,%s>' % (self.username,self.fullname,self.email,self.created_date)


class Notification(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), index=True)
	type_ = db.Column(db.String(15), index=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	user =  db.relationship('User', back_populates='notifications',foreign_keys=user_id)
	timestamp = db.Column(db.Float, default=time.time())
	message = db.Column(db.Text)
	params = db.Column(db.Text)
	sent = db.Column(db.Boolean, default=False)
	
	def __repr__(self):
		return '<Notification: {}>'.format(self.name)


class Role(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), index=True, unique=True)
	created_date = db.Column(db.DateTime)
	active = db.Column(db.Boolean)

	def __repr__(self):
		return '<Role %s,%s,%s>' % (self.name,self.created_date,self.active)


class Pos(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	pos_ = db.Column(db.String(32),unique=True)
	created_date = db.Column(db.Date)
	progress = db.Column(db.String(20))
	company_id = db.Column(db.Integer,db.ForeignKey('company.id'))
	company = db.relationship('Company', back_populates='pos',foreign_keys=company_id)
	active = db.Column(db.Boolean,default=True)
	orders = db.relationship('Order')

	def __repr__(self):
		return '<Pos %s,%s,%s>' % (self.pos_,self.created_date,self.progress)


class Session(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	session_ = db.Column(db.String(32),index=True)
	created_date = db.Column(db.Date)
	active = db.Column(db.Boolean)

	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	user = db.relationship('User',back_populates="sessions",foreign_keys=user_id)

	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	company = db.relationship('Company',back_populates="sessions")

	# pos = db.relationship('Pos')

	def __repr__(self):
		return '<Session %s,%s,%s,%s,%s>' % (self.session_,self.created_date,self.active,self.user_id,self.company_id)

class Payment(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	pos_id = db.Column(db.String(64))
	name = db.Column(db.String(64),index=True)
	amount_due = db.Column(db.Float)
	amount_tended = db.Column(db.Float)
	change = db.Column(db.Float)
	voided = db.Column(db.Boolean)
	created_date = db.Column(db.DateTime)
	
	order_id = db.Column(db.Integer,db.ForeignKey('order.id'),nullable=True)
	order = db.relationship('Order',back_populates="payments",foreign_keys=order_id)

	payment_type_id = db.Column(db.Integer,db.ForeignKey('payment_type.id'),nullable=True)
	payment_type = db.relationship("PaymentType")

	def __repr__(self):
		return '<Payment %s,%s,%s,%s,%s,%s>' % (self.name,self.voided,self.order_amount,self.order_id,self.payment_type_id,self.created_date)


class PaymentType(db.Model):
	id = db.Column(db.Integer, primary_key = True) 
	name = db.Column(db.String(64),index=True,unique=True)
	description = db.Column(db.String(254),index=True,unique=True)
	created_date = db.Column(db.DateTime)
	active = db.Column(db.Boolean)

	def __repr__(self):
		return '<PaymentType %s,%s,%s,%s>' % (self.name,self.description,self.created_date,self.active)	

class Customer(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64),index=True)
	customer_type = db.Column(db.String(254),index=True)
	company_name = db.Column(db.String(254),index=True)
	created_date = db.Column(db.DateTime)
	last_business = db.Column(db.DateTime)
	street = db.Column(db.String(254))
	street2 = db.Column(db.String(254))
	city = db.Column(db.String(254))
	zip_code = db.Column(db.String(254))
	active = db.Column(db.Boolean)
	contact = db.Column(db.String(100))
	barcode = db.Column(db.String(254))
	credit_limit = db.Column(db.Float)
	tax_id = db.Column(db.String(50))
	avatar = db.Column(db.String(324))
	default_ = db.Column(db.Boolean)
	company_id = db.Column(db.Integer,db.ForeignKey('company.id'),nullable=True)
	# company = db.relationship("Company",back_populates="customers")
	# products = db.relationship("Product")
	orders = db.relationship("Order")
	email = db.Column(db.String(120),db.ForeignKey('user.email'),nullable=True)
	user = db.relationship("User",back_populates="customer",foreign_keys=email)
	fav_companies = db.relationship("FavouriteCompany")
	fav_products = db.relationship("FavouriteProduct")

	def get_activation_token(self, expires_in=600):
		return jwt.encode({'customer_activation': self.id, 'exp': time.time() + expires_in},conf.SECRET_KEY, algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_activation_token(token):
		try:
			id = jwt.decode(token, conf.SECRET_KEY, algorithms=['HS256'])['customer_activation']
		except:
			return
		return Customer.query.get(id)

	def __repr__(self):
		return '<Customer %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s>' % (self.name,self.email,self.created_date,self.last_business,self.street,self.street2,self.city,self.zip_code,self.active,self.customer_type,self.company_name,self.contact,self.barcode,self.credit_limit,self.tax_id,self.avatar,self.company_id)


class FavouriteCompany(db.Model):
	id = db.Column(db.Integer, primary_key = True) 
	company_id = db.Column(db.Integer,db.ForeignKey('company.id'), nullable=True)
	customer_id =  db.Column(db.Integer,db.ForeignKey('customer.id'),nullable=False)
	customer = db.relationship("Customer",back_populates="fav_companies",foreign_keys=customer_id)
	company = db.relationship("Company",back_populates="favourites",foreign_keys=[company_id,customer_id])

class FavouriteProduct(db.Model):
	id = db.Column(db.Integer, primary_key = True) 
	company_id = db.Column(db.Integer,db.ForeignKey('company.id'), nullable=True)
	customer_id =  db.Column(db.Integer,db.ForeignKey('customer.id'),nullable=False)
	product_id = db.Column(db.Integer,db.ForeignKey('product.id'))
	customer = db.relationship("Customer",back_populates="fav_products",foreign_keys=customer_id)
	product = db.relationship("Product",back_populates="favourites",foreign_keys=[company_id,product_id])


class Order(db.Model):
	id = db.Column(db.Integer, primary_key = True) 
	name = db.Column(db.String(64),index=True)
	order_date = db.Column(db.DateTime)
	
	tax_amount = db.Column(db.Float,default=0)
	disc_amount = db.Column(db.Float,default=0) 
	sub_total = db.Column(db.Float,default=0) 
	total = db.Column(db.Float,default=0) 
	amount_due = db.Column(db.Float,default=0) 

	filter_state = db.Column(db.String(164),default="not sent")

	prints = db.Column(db.Integer, default=0)
	paid = db.Column(db.Boolean, default=0)
	status = db.Column(db.Integer, default=0)
	barcode = db.Column(db.String(254), index=True,unique=True,nullable=True)
	company_id = db.Column(db.Integer,db.ForeignKey('company.id'))
	company = db.relationship('Company',back_populates="orders",foreign_keys=company_id)

	customer_id =  db.Column(db.Integer,db.ForeignKey('customer.id'),nullable=True)
	customer = db.relationship('Customer',back_populates="orders",foreign_keys=customer_id)

	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	user = db.relationship('User',back_populates="orders",foreign_keys=user_id)

	pos_id = db.Column(db.Integer,db.ForeignKey('pos.id'))
	pos = db.relationship('Pos',back_populates="orders",foreign_keys=pos_id)

	orderlines = db.relationship("OrderLine")
	payments = db.relationship('Payment')

	def __repr__(self):
		return '<Order %s,%s,%s,%s,%s,%s,%s,%s,%s>' % (self.tax_amount,self.disc_amount,self.sub_total,self.amount_due,self.user_id,self.company_id,self.order_date,self.name,self.prints)

class OrderLine(db.Model):
	id = db.Column(db.Integer, primary_key = True) 
	name = db.Column(db.String(64), default="base")
	qty = db.Column(db.Float)
	price = db.Column(db.Float)
	tax = db.Column(db.Float, default=0)
	extended = db.Column(db.Float)
	orderline_date = db.Column(db.DateTime)
	voided = db.Column(db.Boolean)
	discount = db.Column(db.Float)
	order_id = db.Column(db.Integer,db.ForeignKey('order.id'))
	order = db.relationship('Order',back_populates="orderlines",foreign_keys=order_id)
	product_id = db.Column(db.String(20),db.ForeignKey('product.item_code'))
	product = db.relationship('Product',back_populates="orderline",foreign_keys=product_id)

	def __repr__(self):
		return '<OrderLine %s,%s,%s,%s,%s,%s,%s,%s>' % (self.order_id,self.product_id,self.orderline_date,self.name,self.qty,self.discount,self.price,self.extended)

class Product(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	item_code = db.Column(db.String(20), index=True)
	barcode = db.Column(db.String(254), index=True,nullable=True)
	created_date = db.Column(db.DateTime)
	name = db.Column(db.String(84))
	description = db.Column(db.String(254))
	status = db.Column(db.Boolean)
	cost = db.Column(db.Float,default=0)
	price = db.Column(db.Float)
	qty = db.Column(db.Float)
	taxable = db.Column(db.Boolean)
	image = db.Column(db.String(1024))

	company_id = db.Column(db.Integer,db.ForeignKey('company.id'))
	company = db.relationship("Company",back_populates="products")
	
	uoms = db.relationship("UomShedule")
	categories = db.relationship("CategoryProduct")
	variants = db.relationship("Variation")
	orderline = db.relationship("OrderLine")
	favourites = db.relationship("FavouriteProduct")
	images = db.relationship("ProductPhoto")
	def as_dict(self):
	   return {f.name: getattr(self, f.name) for f in self.__table__.columns}

	def __repr__(self):
		return '<Product %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s>' % (self.item_code,self.name,self.description,self.taxable,self.qty,self.price,self.cost,self.image,self.company_id,self.barcode,self.created_date,self.status)

class Variation(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	product_id = db.Column(db.Integer,db.ForeignKey('product.id'))
	name = db.Column(db.String(64),index=True)
	price = db.Column(db.Float)
	qty = db.Column(db.Float)
	created_date = db.Column(db.DateTime)
	
	def __repr__(self):
		return '<Variation %s,%s,%s,%s,%s,%s>' % (self.product_id,self.name,self.created_date,self.active,self.price,self.taxable)


class Company(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64),index=True,unique=True)
	email = db.Column(db.String(120), index=True)
	created_date = db.Column(db.DateTime)
	logo = db.Column(db.String(254),default=None)
	store_front_image = db.Column(db.String(254),default=None)
	tax = db.Column(db.Float)
	location = db.Column(db.String(1024))
	contact = db.Column(db.String(11))
	thank_note = db.Column(db.String(250))
	active = db.Column(db.Integer)
	closed = db.Column(db.Integer, default=1)
	published = db.Column(db.Integer, default=0)
	paused = db.Column(db.Integer, default=0)
	twitter = db.Column(db.String(250), default=None)
	google = db.Column(db.String(250), default=None)
	instagram = db.Column(db.String(250), default=None)
	facebook = db.Column(db.String(250), default=None)
	order_hold_limit = db.Column(db.Integer, default=1)
	coords = db.Column(db.String(30), default=None)
	plan_id = db.Column(db.Integer,db.ForeignKey('plan.id'))
	plan = db.relationship("Plan",back_populates="company", foreign_keys=plan_id) 
	owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	owner = db.relationship("User",back_populates="company", foreign_keys=owner_id) 
	
	company_type_id = db.Column(db.Integer,db.ForeignKey('company_type.id'))
	company_type = db.relationship("CompanyType",back_populates="companies",foreign_keys=company_type_id) 
	
	# customers = db.relationship("Customer",back_populates="company")
	categories = db.relationship("CompanyCategory")
	products = db.relationship("Product")
	sessions = db.relationship("Session")
	favourites = db.relationship("FavouriteCompany")
	orders = db.relationship("Order")
	line = db.relationship("Vline")
	pos = db.relationship("Pos")


	def get_activation_token(self, expires_in=600):
		return jwt.encode({'company_activation': self.id, 'exp': time.time() + expires_in},conf.SECRET_KEY, algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_activation_token(token):
		try:
			id = jwt.decode(token, conf.SECRET_KEY, algorithms=['HS256'])['company_activation']
		except:
			return
		return Company.query.get(id)

	def as_dict(self):
	   return {f.name: getattr(self, f.name) for f in self.__table__.columns}

	def __repr__(self):
		return '<Company %s,%s,%s,%s,%s,%s,%s,%s>' % (self.name,self.logo,self.tax,self.active,self.owner_id,self.email,self.company_type_id,self.location)


class Plan(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(20),index=True,unique=True)
	cost = db.Column(db.Float)
	details = db.Column(db.String(1024))
	created_date = db.Column(db.DateTime)
	company = db.relationship('Company')
	
	def __repr__(self):
		return '<Plan %s,%s>'%(self.name,self.cost)

class Companies(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	company_id = db.Column(db.Integer,db.ForeignKey('company.id'))
	company = db.relationship('Company')
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	# user = db.relationship('User',back_populates="companies",foreign_keys=user_id)
	
	def __repr__(self):
		return '<Company %s>'%(self.company_id)


class CompanyType(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64),index=True,unique=True)
	image = db.Column(db.String(100))
	created_date = db.Column(db.DateTime)
	active = db.Column(db.Boolean)
	companies = db.relationship("Company")

	def __repr__(self):
		return '<CompanyType %s,%s,%s>' % (self.name,self.created_date,self.active)


class ProductType(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64),index=True,unique=True)
	created_date = db.Column(db.DateTime)
	active = db.Column(db.Boolean)
	# products = db.relationship("Product",back_populates="product_type")

	def __repr__(self):
		return '<ProductType %s,%s,%s>' % (self.name,self.created_date,self.active)


class ProductPrices(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	item_code = db.Column(db.String(254),db.ForeignKey('product.item_code'))
	company_id = db.Column(db.Integer,db.ForeignKey('company.id'))
	created_date = db.Column(db.DateTime)
	price  = db.Column(db.Float)

	def __repr__(self):
		return '<ProductPrices %s,%s,%s,%s>' % (self.item_code,self.company_id,self.created_date,self.cost)


class Uom(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64),index=True,unique=True)
	uom = db.Column(db.Float)
	base = db.Column(db.Integer)
	conversion = db.Column(db.Float)
	created_date = db.Column(db.DateTime)
	active = db.Column(db.Boolean)
	shedules = db.relationship("UomShedule")
	def __repr__(self):
		return '<UnitOfMeasure %s,%s,%s,%s,%s,%s>' % (self.name,self.uom,self.created_date,self.active,self.conversion,self.base)

class UomShedule(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	uom_id = db.Column(db.Integer,db.ForeignKey('uom.id'))
	uom = db.relationship("Uom",back_populates="shedules",foreign_keys=uom_id)
	product_id = db.Column(db.Integer,db.ForeignKey('product.id'))
	def __repr__(self):
		return '<UomShedule %s,%s>' % (self.uom_id,self.product_id)

class Category(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64),index=True)
	created_date = db.Column(db.DateTime)
	image = db.Column(db.String(1024))
	active = db.Column(db.Boolean)
	parent_id = db.Column(db.Integer, db.ForeignKey('category.id'),default=None)
	products = db.relationship("CategoryProduct")
	companies = db.relationship("CompanyCategory")

	def __repr__(self):
		return '<Category %s,%s,%s>' % (self.name,self.created_date,self.active)

class CompanyCategory(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
	category = db.relationship("Category") 
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	company = db.relationship("Company") 
	
	def __repr__(self):
		return '<CompanyCategory %s,%s>' % (self.category_id,self.company_id)


class CategoryProduct(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	category_id = db.Column(db.Integer,db.ForeignKey('category.id'))
	category = db.relationship("Category") 
	product_id = db.Column(db.Integer,db.ForeignKey('product.id'))
	product = db.relationship("Product")

	def __repr__(self):
		return '<CategoryProduct %s,%s>' % (self.category_id,self.product_id)

class Discount(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	reason = db.Column(db.String(264),index=True)
	name = db.Column(db.String(64),index=True)
	amount = db.Column(db.Float)
	created_date = db.Column(db.DateTime)

	def __repr__(self):
		return '<Discount %s,%s,%s,%s>' % (self.reason,self.name,self.amount,self.created_date)

class Subscriber(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(150),index=True,unique=True)
	created_date = db.Column(db.DateTime)

	def __repr__(self):
		return '<Subscriber %s,%s>' % (self.email,self.created_date)

class Vline(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	company_id = db.Column(db.Integer,db.ForeignKey('company.id'))
	created_date = db.Column(db.Date)
	serving = db.Column(db.Integer)
	active = db.Column(db.Boolean)
	company = db.relationship('Company')
	lineup =  db.relationship('Vlineup')
	def __repr__(self):
		return '<Vline %s,%s,%s,%s>' % (self.company_id,self.serving,self.created_date,self.active)

class Vlineup(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	line_id = db.Column(db.Integer,db.ForeignKey('vline.id'))
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	company_id = db.Column(db.Integer,db.ForeignKey('company.id'))
	joined = db.Column(db.DateTime)
	status = db.Column(db.Integer)
	place_in_line = db.Column(db.Integer)
	user = db.relationship('User')
	vline = db.relationship('Vline')
	
	def __repr__(self):
		return '<Vlineup %s,%s,%s,%s>' % (self.user_id,self.company_id,self.joined,self.place_in_line)

class VlineHistory(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	vline = db.Column(db.Integer)
	company_id = db.Column(db.Integer,db.ForeignKey('company.id'))
	created_date = db.Column(db.Date)

	def __repr__(self):
		return '<VlineHistory %s,%s,%s,%s>' % (self.user_id,self.company_id,self.created_date,self.place_in_line)

class ProductPhoto(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	product_id =  db.Column(db.Integer, db.ForeignKey('product.id'))
	product =  db.relationship('Product',back_populates="images",foreign_keys=product_id)
	company_id =  db.Column(db.Integer, db.ForeignKey('company.id'))
	position = db.Column(db.Integer)
	image =  db.Column(db.String(128))

	def __unicode__(self):
		return self.image

	def save_image(self, file_obj):
		self.image = secure_filename(file_obj.filename)
		full_path = os.path.join(conf.PRODUCT_IMAGES_DIR, self.image)
		file_obj.save(full_path)
		self.save()

	def url(self):
		return os.path.join(conf.PRODUCT_IMAGES_DIR, self.image)

	def thumb(self):
		return Markup(f'<img src="{self.url()}" style="height: 80px;" />')

	def __repr__(self):
		return f'<Photo: {self.image}>'