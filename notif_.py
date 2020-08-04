#!/usr/bin/python3
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from app.models import Notification, User, Customer, Company
from app.func_ import *
from datetime import datetime
# import app 
import smtplib
import os
import config as conf
import simplejson as json

app = Flask(__name__)
db = SQLAlchemy()
db.init_app(app)
app.config.from_object('config')
app.app_context().push()

notifs_ = Notification.query.filter_by(sent=0).all()
error = None
errors = []
sent_emails = []


def notify_(notif):
	error = {"error":"No notification to process"}
	if notif.name == "activation":
		account = DDOT(json.loads(notif.params))
		error = accountVerification(account)
	else:
		if notif.name == "recovery":
			account = DDOT(json.loads(notif.params))
			error = recoverUserAccount(account)
		else:
			if notif.name == "confirmation":
				account = DDOT(json.loads(notif.params))
				error = sendOrderConfirmation(account)

	return error


if notifs_:
	for notif in notifs_:
		res = notify_(notif)
	
		if "success" in res:
			user_ = User.query.filter_by(id=notif.user_id).first()
			user_.update_notification_sent_flag(notif.id,1)
			sent_emails.append(user_.email)
		else:
			errors.append(res["error"])


# datetime object containing current date and time
now = datetime.now()
now = now.strftime("%d/%m/%Y %H:%M:%S")	
if sent_emails:
	print("Email sent to: @{}\n".format(now))		
	print(",".join(sent_emails))

if errors:
	for error in errors:
		print(error)
		print("\n")
# else:
	# print("No new emails to send.")
# for file attachment with the email

# filename = "NAME OF THE FILE WITH ITS EXTENSION"
# attachment = open("PATH OF THE FILE", "rb")
 
# part = MIMEBase('application', 'octet-stream')
# part.set_payload((attachment).read())
# encoders.encode_base64(part)
# part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
 
# msg.attach(part)	
