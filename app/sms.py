from textmagic.rest import TextmagicRestClient
import os
import sys

account_sid = os.getenv('SMS_SID')
auth_token = os.getenv('SMS_AUTH')

def sms_(to,msg):
	client = TextmagicRestClient(account_sid, auth_token)
	message = client.messages.create(phones=to, text=msg)

