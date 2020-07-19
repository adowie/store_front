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
import os


command = sys.argv[1]
if command == "-np":
	company = sys.argv[2]
	company_num = sys.argv[3]

if command == "-du":
	user_name = sys.argv[2]
	user_email = sys.argv[3]
	user_full = sys.argv[4]
	user_pass = sys.argv[5]

if command == "-cm":
	owner_name = sys.argv[2]
	company_name = sys.argv[3]
	company_email = sys.argv[4]
	company_logo = sys.argv[5]
	company_sfi = sys.argv[6]
	company_location = sys.argv[7]
	company_contact = sys.argv[8]
	thank_note = sys.argv[9]
	order_time_limit = sys.argv[10]
	coords = sys.argv[11]
	company_type = sys.argv[12]
	plan = sys.argv[13]
	company_tax = sys.argv[14]
	company_pass = sys.argv[15]


DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_SERVER')
DB_USER = os.getenv('DB_USER')
DB_ = os.getenv('DBASE')

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://"+DB_USER+":"+DB_PASS+"@"+DB_HOST+"/"+DB_

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

session = Session()

Base = declarative_base()

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

class Company(Base):
	__tablename__ = 'company'

	id = Column(Integer, primary_key = True)
	name = Column(String(64),index=True,unique=True)
	email = Column(String(120), index=True)
	created_date = Column(DateTime)
	logo = Column(String(254),default=None)
	store_front_image = Column(String(254),default=None)
	location = Column(String(1024))
	contact = Column(String(11))
	thank_note = Column(String(250))
	closed = Column(Integer, default=1)
	published = Column(Integer, default=0)
	paused = Column(Integer, default=0)
	twitter = Column(String(250), default=None)
	google = Column(String(250), default=None)
	instagram = Column(String(250), default=None)
	facebook = Column(String(250), default=None)
	order_hold_limit = Column(Integer, default=60)
	coords = Column(String(30), default=None)
	company_type_id = Column(Integer)
	plan_id = Column(Integer)
	active = Column(Integer)
	owner_id = Column(Integer)
	tax = Column(Float)

	def __init__(self, name, email, created_date, logo, store_front_image, location, contact, company_type_id, owner_id, tax, thank_note="", order_hold_limit=60, coords="0,0", plan_id=1, active=True): 
		self.name = name
		self.email = email
		self.created_date = created_date
		self.logo = logo
		self.store_front_image = store_front_image
		self.location = location
		self.contact = contact
		self.thank_note = thank_note
		self.order_hold_limit = order_hold_limit
		self.coords = coords
		self.company_type_id = company_type_id
		self.plan_id = plan_id
		self.active = active
		self.owner_id = owner_id
		self.tax = tax
	
class Customer(Base):
	__tablename__ = 'customer'

	id = Column(Integer, primary_key = True)
	name = Column(String(64),index=True)
	customer_type = Column(String(254),index=True)
	company_name = Column(String(254),index=True)
	created_date = Column(DateTime)
	last_business = Column(DateTime)
	street = Column(String(254))
	street2 = Column(String(254))
	city = Column(String(254))
	zip_code = Column(String(254))
	active = Column(Boolean)
	contact = Column(String(100))
	barcode = Column(String(254))
	credit_limit = Column(Float)
	tax_id = Column(String(50))
	avatar = Column(String(224), default="img/customers/default.png")
	default_ = Column(Boolean)
	email = Column(String(120))

	def __init__(self, email, name, type_,avatar=None, contact="(876) 000-0000",company_name=None, credit_limit=500, tax_id="000-000-000", created_date=now(), last_business=None, street="", street2="", city="", zip_code="", active=True):
		self.name = name
		self.customer_type = type_
		self.company_name = company_name
		self.created_date = created_date
		self.last_business = last_business
		self.street = street
		self.street2 = street2
		self.city = city
		self.zip_code = zip_code
		self.active = True
		self.contact = contact
		self.barcode = ""
		self.credit_limit = credit_limit
		self.tax_id = tax_id
		self.default_ = False
		self.email = email

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
	image = Column(String(224),default='img/products/default.png')
	company_id = Column(Integer)

	def __init__(self,item_code, created_date, name, description,company_id,image=None, price=0, qty=0, taxable=1,status=0,barcode=None,cost=0):
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
	__tablename__ = "user"

	id = Column(Integer, primary_key=True)
	username = Column(String(20), index=True)
	fullname = Column(String(64), index=True)
	email = Column(String(120), index=True, unique=True)
	password_ = Column(String(220), index=True)
	created_date = Column(DateTime)
	image = Column(String(224), default='img/user/default.png')
	last_login = Column(DateTime)
	is_logged_in = Column(Boolean, default=False)
	is_admin = Column(Boolean, default=False)
	def __init__(self,username,fullname,email,password_, created_date, image=None, last_login=None, is_logged_in=False, is_admin=True):
		self.username = username
		self.fullname = fullname
		self.email = email
		self.password_ = password_
		self.created_date = created_date
		self.image = image
		self.last_login = last_login
		self.is_logged_in = is_logged_in
		self.is_admin = is_admin


def create_company():
	name = owner_name.split(" ")
	user_name = f'{name[1].lower()[0]}{name[1].lower()}'
	db_sess = session

	user = db_sess.query(User).filter_by(email=company_email).first()

	if not user:
		user = User(username=user_name, fullname=owner_name, email=company_email, password_=generate_password_hash(company_pass), created_date=now()) 
	
		try:
			db_sess.add(user)
			db_sess.commit()
			print("Creating company user.....\n")
		except (SQLAlchemyError, IntegrityError, DataError) as e:
			db_sess.rollback()
			db_sess.flush() # for resetting non-commited .add()
			return e

	customer = db_sess.query(Customer).filter_by(email=company_email).first()
	if not customer:
		customer = Customer(email=company_email, name=owner_name, type_="normal")
		try:
			print("Company user created.....\n")
			print("......Now Creating company user as customer.....\n")

			db_sess.add(customer)
			db_sess.commit()
		except (SQLAlchemyError, IntegrityError, DataError) as e:
			db_sess.rollback()
			db_sess.flush() # for resetting non-commited .add()
			return e

	if user:
		company = db_sess.query(Company).filter_by(email=company_email).first()
		if not company:
			company = Company(name=company_name, email=company_email, created_date=now(), logo=company_logo, store_front_image=company_sfi, location=company_location, contact=company_contact, thank_note=thank_note,order_hold_limit=order_time_limit, coords=coords, company_type_id=company_type, plan_id=plan, active=True, owner_id=user.id, tax=company_tax)
			try:
				print("......Created customer account.....\n")
				print("......Now Creating company.....\n")
				db_sess.add(company)
				db_sess.commit()
			except (SQLAlchemyError, IntegrityError, DataError) as e:
				db_sess.rollback()
				db_sess.flush() # for resetting non-commited .add()
				return e
			
			print("......Company created successfully.....\n")
			print(f"......Company Name is: {company.name}\n")
			print(f"......Company ID is: {company.id}\n")
			print(f"......You can initiate the auto product addition script with python3 manual.py -np {''.join(company.name.lower().split())} {company.id}\n")
			print(f"......Ensure that folder with img/company/{''.join(company.name.lower().split())} has been created and populated with product shots.\n")

		else:
			print("......That company email is already taken try using a different one.....\n")
	else:
		print(".....Unknown error caused company not to be created.....\n")

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

		if product_code != "logo" and product_code != "store":
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

if command == "-np":
	print(create_product_from_image())

if command == "-du":
	print(add_default_admin_user())

if command == "-cm":
	print(create_company())


