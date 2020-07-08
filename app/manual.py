from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime,Float,Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from pathlib import Path
from os import listdir, rename
from os.path import isfile, join
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from werkzeug.security import generate_password_hash, check_password_hash

import sys
import shutil
import time


command = sys.argv[1]
if command == "-np":
	company = sys.argv[2]
	company_num = sys.argv[3]

if command == "-du":
	user_name = sys.argv[2]
	user_email = sys.argv[3]
	user_full = sys.argv[4]
	user_pass = sys.argv[5]

engine = create_engine("mysql://Adora:62866181@ali@localhost:3306/osfo")
Session = sessionmaker(bind=engine)

session = Session()

Base = declarative_base()
class Company(Base):
	__tablename__ = 'company'

	id = Column(Integer, primary_key = True)
	name = Column(String(64),index=True,unique=True)
	email = Column(String(120), index=True)
	created_date = Column(DateTime)
	logo = Column(String(254),default=None)
	store_front_image = Column(String(254),default=None)
	tax = Column(Float)
	location = Column(String(1024))
	contact = Column(String(11))
	thank_note = Column(String(250))
	active = Column(Integer)
	closed = Column(Integer, default=1)
	published = Column(Integer, default=0)
	paused = Column(Integer, default=0)
	twitter = Column(String(250), default=None)
	google = Column(String(250), default=None)
	instagram = Column(String(250), default=None)
	facebook = Column(String(250), default=None)
	order_hold_limit = Column(Integer, default=1)
	coords = Column(String(30), default=None)
	# plan_id = Column(Integer,ForeignKey('plan.id'))
	# plan = relationship("Plan",back_populates="company", foreign_keys=plan_id) 
	# owner_id = Column(Integer,ForeignKey('user.id'))
	# owner = relationship("User",back_populates="company", foreign_keys=owner_id) 
	
	# company_type_id = Column(Integer,ForeignKey('company_type.id'))

class Product(Base):
	__tablename__ = 'product'
	id = Column(Integer, primary_key = True)
	item_code = Column(String, index=True)
	barcode = Column(String, index=True,nullable=True)
	created_date = Column(DateTime)
	name = Column(String)
	description = Column(String)
	status = Column(Boolean)
	cost = Column(Float)
	price = Column(Float)
	qty = Column(Float)
	taxable = Column(Boolean)
	image = Column(String)

	company_id = Column(Integer,ForeignKey('company.id'))
	def __init__(self,item_code, created_date, name, description,image,company_id, price=0, qty=0, taxable=1,status=0,barcode=None,cost=0):
		self.item_code = item_code
		self.barcode = barcode
		self.created_date = created_date
		self.name = name
		self.description = description
		self.status = status
		self.cost = cost
		self.price = price
		self.qty = qty
		self.taxable = taxable
		self.image = image
		self.company_id = company_id

class User(Base):
	__tablename__ = users

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
	def __init__(self,username,fullname,email,password_, created_date, image, last_login=None, is_logged_in=False, is_admin=True):
		self.username = username
		self.fullname = fullname
		self.email = email
		self.password_ = password_
		self.created_date = created_date
		self.image = image
		self.last_login = last_login
		self.iself.s_logged_in = is_logged_in
		self.is_admin = is_admin

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

def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def db_insert(db_obj):
    error = None
    if len(db_obj) > 0:
        db_sess = session
        try:
            db_sess.bulk_save_objects(db_obj, return_defaults=True)
            for obj_ in db_obj:
                assert obj_.id is not None
            db_sess.commit()
        except (SQLAlchemyError, IntegrityError, DataError) as e:
            db_sess.rollback()
            db_sess.flush() # for resetting non-commited .add()
            error = e
        if error:
            error = "Error: %s"%error
        return error
    return "Error: No entry to process!"

def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")

# create business
# auto create user and customer

# bulk product adder by product image
def create_product_from_image():
	mypath = f'img/company/{company}'
	base = 'static/'
	images = [f for f in listdir(f'{base}{mypath}') if isfile(join(f'{base}{mypath}', f))]
	bulk_products = []
	for image in images:
		old_image = image
		product_id = image.split("_")
		image_path = f'{mypath}/{image}'
		if len(product_id) > 1:
			shutil.move(f'{base}{mypath}/{image}',f'{base}{mypath}/{product_id[1]}')
			image_path = f'{mypath}/{product_id[1]}'
			product_code = product_id[1][:-4]
		else:
			product_code = product_id[0][:-4]

		product = Product(item_code=product_code,created_date=now(),name=old_image[:-4],description='',image=image_path,company_id=company_num)
		bulk_products.append(product)
	return db_insert(bulk_products)
		
def add_default_admin_user():
	user = User(username=user_name, fullname=user_full, email=user_email, password=user_pass, created_date=now()) 
	db_sess = session
	try:
		db_sess.add(user)
		db_sess.commit()
	except (SQLAlchemyError, IntegrityError, DataError) as e:
		db_sess.rollback()
		db_sess.flush() # for resetting non-commited .add()
		error = e




print(get_product_images())