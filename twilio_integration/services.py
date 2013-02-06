from django.conf import settings
from twilio.rest import TwilioRestClient
import urllib2
import urllib
import re

def send_text(number, message, twilio=False):
    """ Sends a text message """
    number = re.sub(r'\D', '', number)
    if len(number) < 10:
        print 'number too short'
        return
    if len(number) < 11:
        number = '1' + number
    print number
    if twilio:
        send_text_twilio(number, message)
    else:
        send_text_tropo(number, message)

def send_text_twilio(number, message, fromnumber=settings.DEFAULT_FROM_NUMBER):
    fromnumber = '+' + re.sub(r'\D', '', fromnumber)
    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.sms.messages.create(body=message, to=number, from_=fromnumber)
    print message.sid

def send_text_tropo(number, message):
    """ Add the following to a hostedfile test.php
    <?php
    _log('Number To Call:'.$numToCall);
    _log('Payload:'.$payload);
    call('+'.$numToCall, array('network'=>'SMS'));
    say($payload);
    ?>
    """
    url = 'http://api.tropo.com/1.0/sessions'
    values = {
            'action': 'create', 
            'token': settings.TROPO_AUTH_TOKEN,
            'numToCall': number,
            'payload': message,
        }
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    print response.read()
