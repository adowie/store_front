# error = None
	# if pos_session:
	# 	if len(pos_session.orders) > 1:
	# 		return True,pos_session
	# 	else:
	# 		if len(pos_session.orders) > 0:
	# 			for order in pos_session.orders:
	# 				if len(order.orderlines) > 0:
	# 					return True,pos_session
	# 				else:
	# 					order_ = Order.query.filter_by(id=order.id,pos_id=order.pos_id,user_id=order.user_id).first()
	# 					pos_session.progress = "notused"
	# 					error = db_commit_delete_or_revert(order_)
	# 					# if not error:
	# 					# 	error = db_commit_add_or_revert(pos_session)
	# 					# 	if not error:
	# 					# 		return False,None
	# 					# 	else:
	# 					# 		print(error)
	# 					# else:
	# 					# 	print(error)
	# 		else:
	# 			return True,pos_session
	# else:
	# 	return False,None

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