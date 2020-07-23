from flask import flash, redirect, render_template, url_for,request,session
from flask_login import login_required, login_user, logout_user,current_user
from threading import Thread
from datetime import datetime
from Crypto.Cipher import AES
from . import db
from .models import User,Customer,Product

import jwt
import config as conf
import smtplib
import asyncore
import time
import os
import base64
import random

def fetch_company_products(company):
	active_products = len(Product.query.filter_by(company_id=company,status=True).all())
	inactive_products = len(Product.query.filter_by(company_id=company,status=False).all())
	return active_products, inactive_products

def getFavourites(user):
	customer_ = Customer.query.filter_by(email=user).first()
	companies = 0
	products = 0
	if customer_:
		companies = len(customer_.fav_companies)
		products = len(customer_.fav_products)
	return products + companies
	
def year():
	return time.strftime("%Y")

def now_time():
	return time.strftime("%H:%M")

def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def today():
    return time.strftime("%Y-%m-%d")


def boolInts(int_):
	if int_ == 1:
		return True
	else:
		return False

def datetimeToTime(dt):
    return dt.strftime('%H:%M:%S')

def datetimeToDate(dt):
	if dt:
		day = dt.strftime('%Y-%m-%d')
		return day
   

def convertDateTime(dt):
	if dt:
		return datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')

def barCoder(code):
    if code and code != "":
    	return code
    #     c = md5.new()
    #     c.update(code)
    #     return c.digest()
    # else:
    #     return None
    return  None

def save_uploaded_file (file_, upload_dir):
    # This saves a file uploaded by an HTML form.
    #    The form_field is the name of the file input field from the form.
    #    For example, the following form_field would be "file_1":
    #        <input name="file_1" type="file">
    #    The upload_dir is the directory where the file will be written.
    #    If no file was uploaded or if the field does not exist then
    #    this does nothing.
    
    fileitem = file_

    filename = upload_dir + "default.png";

    if fileitem and type(fileitem) != str:
        if fileitem.filename:
            extension = os.path.splitext(fileitem.filename)[1][1:].strip()
            fn = str(randomString(13))+"."+extension
            filename = upload_dir + fn 

            fout = open(os.path.join(upload_dir, fn), 'wb')
           
            while 1:
                chunk = fileitem.read(100000)
                if not chunk: break
                fout.write (chunk)
            fout.close()
    
    supd = filename.split("/")
    realPath = "/".join(supd[2:])

    return str(realPath)

def wpos_error_(msg):
    return msg


def trim(str_):
    return str_.replace(" ","")

def encrypt_decrypt(ed,enc_str):
    if ed == "d":
        cipher = AES.new(conf.SECRET_KEY,AES.MODE_ECB)
        return cipher.decrypt(base64.b64decode(enc_str)).strip()
    elif ed == "e":
        cipher = AES.new(conf.SECRET_KEY,AES.MODE_ECB) # never use ECB in strong systems obviously
        return base64.b64encode(cipher.encrypt(enc_str.rjust(32)))
    else:
        return 0


def randomString(_len):
    id_ = "";
    cypher_ = [];
    cypher = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

    for i in range((len(cypher) -1)):
        cypher_.append(cypher[i])

    for i in range(_len):
        id_ += cypher_[ int(round(random.randint(0, (len(cypher_) -1) ))) ]

    return id_


# make dictionary key,value referenceable by dot '.' notation
class DDOT(dict):
     # Usage: arr = DDOT(dict)
     # keyvalue = arr.key
    def __init__(self, *args, **kwargs):
        super(DDOT, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(DDOT, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(DDOT, self).__delitem__(key)
        del self.__dict__[key]

def db_insert(db_obj):
    error = None
    if len(db_obj) > 0:
        db_sess = db.session
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

def commitObjectToDB(obj_):
	error = None
	try:
		# add object to the database
		db.session.add(obj_)
		db.session.commit()
	except SQLAlchemyError as e:
		db.session.rollback()
		db.session.flush() # for resetting non-commited .add()
		error = e 

	if error:
		return {'error': error}

	return {'obj': obj_ }

def send_async_email(login,password,from_addr,to_addr_list,msg):

	server = smtplib.SMTP(smtpserver)
	server.starttls()
	try:
		server.login(login,password)
		server.sendmail(from_addr, to_addr_list, msg.as_string())	
	except Exception as e:
		return {"error": e}
	server.quit()

def sendMail(from_addr, to_addr_list, cc_addr_list, subject, text_message,html_message, login, password):
	from email.mime.image import MIMEImage
	from email.mime.text import MIMEText
	from email.mime.multipart import MIMEMultipart
	# headers
	msg = MIMEMultipart('alternative')
	msg['To'] = '%s' % ','.join(to_addr_list) 
	msg['From'] = from_addr
	msg['Subject'] = subject
	msg['In-Reply-To'] = conf.COMPANY_EMAIL
	msg.add_header('reply-to', conf.COMPANY_EMAIL)
	
	text = text_message
	html = html_message

	texta_ = MIMEText(text, 'plain') #text alternative
	htmla_ = MIMEText(html, 'html') #html alternative
	
	msg.attach(texta_)
	msg.attach(htmla_)

	if conf.SEND_EMAIL:
		loop_thread = Thread(target=asyncore.loop, name="Asyncore Loop for smtplib sendmail")
		# If you want to make the thread a daemon
		loop_thread.daemon = True
		loop_thread.start()
		
		server = smtplib.SMTP(conf.MAIL_SERVER, conf.MAIL_PORT)
		server.starttls()

		try:
			if conf.SEND_EMAIL:
				server.login(login,password)
				server.sendmail(from_addr, to_addr_list, msg.as_string())
			
		except Exception as e:
			return {"error": e}

		server.quit()
	return {"success":None}


def resetUserPassword(passwd,token):
	user = User.verify_recover_password_token(token)
	if not user:
		return {"token":"Invalid Token"}
	else:
		user.password_ = passwd
		try:
			db.session.commit()
		except:
			return

	return {"success":""}


def recoverUserAccount(account):
	# user_ = User.query.filter_by(email=account.email_).first()
	# if module == "auth":
	# 	login_uri = 'auth.login'
	# 	recover_uri = 'auth.recover'
	# else:
	# 	if module == "osf":
	# 		login_uri = 'osf.account'
	# 		recover_uri = 'osf.recover'

			# url_for(login_uri,_external=True)
			# url_for(recover_uri,token=token,_external=True)

	if account:
		error = None
		admin_error = None
		_temp = None
		try:
			_temp = get_email_template('recovery_temp.html',{"user_":account.name,"app_link":account.app_link,"rec_link":account.rec_link,"app_sign":"Our Store Front Online"})	
		except Exception as e:
			error = {"error": e.message }

		if _temp:
		# else:
			rec_temp = _temp
			if user_:
		# 		pass
				try:
					error = sendMail(conf.ADMINS[0],[account.email],[],"Account Recovery","To recover your account copy the following link to your browsers address bar %s"%recover_url,rec_temp,conf.MAIL_USERNAME,conf.MAIL_PASSWORD)
				except Exception as e:
					error = {"error": e}
			else:
				error = {"error":"That email address is not associated with any user accounts. Please contact support if you believe this to be a mistake."}
		else:
			temp_error = """\
			 				<html>
			 				<head></head>
			 				<body> %s </body>
			 				</html>
			 			 """ % error["error"]
			admin_error = sendMail(conf.ADMINS[0],[conf.ADMINS[1]],[],"Template Error:",error["error"],temp_error,conf.MAIL_USERNAME,conf.MAIL_PASSWORD)
		if admin_error:
			return {"success": "An email has been sent to the address you provided with instructions on how to recover your account. If you do not receive this email in the next 5 minutes please try again and report issue if multiple failed attemps."}
		else:
			if 'success' in error:
				return {"success": "An email has been sent to the address you provided with instructions on how to recover your account."}
	else:
		error = {'error':'Account does not exist.'}
	return error

def accountVerification(account):
	error = None
	_temp = None
	act_temp = ""
			
	if account:
		try:
			_temp = get_email_template('activation_temp.html',{"user_":account.name,"app_link":account.app_link,"rec_link":account.rec_link,"app_sign":"Our Store Front Online","account_type":account.type.capitalize()})	
		except Exception as e:
			error = {"error": e }
		
		if _temp:
			act_temp = _temp
		
		try:
			error = sendMail(conf.ADMINS[0],[account.email],[],"Account Activation","To activate your account copy the following link to your browsers address bar %s"%account.rec_link,act_temp,conf.MAIL_USERNAME,conf.MAIL_PASSWORD)
		except Exception as e:
			error = {"error": e}
	else:
		error = {'error':'Account does not exist.'}
	return error

def sendOrderConfirmation(account):
	error = None
	_temp = None 

	account_name = account.name
	confirmation_message = account.message 
	confirmation_email = account.email
	rec_link =  account.rec_link
	app_link = account.app_link
	# if type_ == "confirmed":
	# 	account_name = order.company.name
	# 	confirmation_message = f"You have a new order confirmation. Order#{order.id} has been confirmed by customer and requires fulfillment. Log in to your OSFO account for order detail using the button below."
	# 	rec_link = url_for('home.dashboard',_external=True)
	# 	confirmation_email = order.company.email
	# else:
	# 	if type_ == "fulfilled":
	# 		account_name = order.customer.name
	# 		confirmation_message = f"Your order has been fulfilled. Order#{order.id} has been confirmed [fulfilled] by #{order.company.name}. You can now pickup your items and complete transaction @ store location. Company details can be acquired by clicking the button below."
	# 		rec_link = url_for('osf.company',name=order.company.name,_id=order.company.id,_external=True)
	# 		confirmation_email = order.customer.email
	
	try:
		_temp = get_email_template('confirmation_temp.html',{"user_":account_name,"app_link":app_link,"rec_link":rec_link,"app_sign":"Our Store Front Online","confirmation_message":confirmation_message})	
	except Exception as e:
		error = {"error": e}
		
	if _temp:
		act_temp = _temp
	
	try:
		error = sendMail(conf.ADMINS[0],[confirmation_email],[],"Order Confirmation",confirmation_message,act_temp,conf.MAIL_USERNAME,conf.MAIL_PASSWORD)
	except Exception as e:
		error = {"error": e}
	
	return error

# def Notification(notif_):
# 	error = None
# 	_temp = None
	
# 	try:
# 		_temp = get_email_template('notification_temp.html',{"user_":notif_.name,"app_link":url_for('osf.land',_external=True),"app_sign":"Our Store Front Online"})	
# 	except Exception as e:
# 		error = {"error": e }
	
# 	if _temp:
# 		not_temp = _temp
	
# 	try:
# 		error = sendMail(conf.ADMINS[0],[account.email],[],"Notification","This is a notification email from OSFO",not_temp,conf.MAIL_USERNAME,conf.MAIL_PASSWORD)
# 	except Exception as e:
# 		error = {"error": e}

# 	return error

def sendRegistrationLink(user):
	pass


def get_email_template(temp_,vargs):
	return render_template('email_/'+temp_,**vargs)
	

def loginPOSUser(form):
	user_ = User.query.filter_by(email=form.email.data).first()
	if user_ is not None and user_.verify_password(form.password.data):
		return user_
	return None


# grant user access
def addUserCompanyAccess(obj_):
    error = ""
  
    access = Companies( user_id = obj_.user, company_id = obj_.company )
    error = commitObjectToDB(access)

    return error


def company_required(func):
	def company():
		if "company" in session:
			func()
		else:
			return redirect(url_for('auth.company'))
	return company