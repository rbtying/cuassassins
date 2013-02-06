from django.conf import settings
from twilio.rest import TwilioRestClient
import re

def send_text(number, message, twilio=True):
    """ Sends a text message """
    send_text_twilio(number, message)

def send_text_twilio(number, message, fromnumber=settings.DEFAULT_FROM_NUMBER):
    number = re.sub(r'\D', '', number)
    fromnumber = '+' + re.sub(r'\D', '', fromnumber)
    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.sms.messages.create(body=message, to=number, from_=fromnumber)
    print message.sid
