from textmagic.rest import TextmagicRestClient
import os
import sys

account_sid = os.getenv('SMS_SID')
auth_token = os.getenv('SMS_AUTH')

client = TextmagicRestClient(account_sid, auth_token)
to = sys.argv[1]
msg = sys.argv[2]
message = client.messages.create(phones=to, text=msg)

print(message)