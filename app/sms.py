from textmagic.rest import TextmagicRestClient
import os
import sys

account_sid = os.getenv('SMS_SID')
auth_token = os.getenv('SMS_AUTH')

def sms_(to,msg):
	client = TextmagicRestClient(account_sid, auth_token)
	error = None
	try:
		message = client.messages.create(phones=to, text=msg)
		error = {"success":f"SMS notication has been sent to {to}"}
	except Exception as e:
		error = {"error": e}
	return error

