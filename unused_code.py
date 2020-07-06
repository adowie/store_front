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