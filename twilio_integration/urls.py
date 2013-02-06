from django.conf.urls.defaults import *

urlpatterns = patterns('twilio_integration.views',
        url(r'^send_code/$', 'send_code', name='send_code'),
        url(r'^verify_code/$', 'verify_code', name='verify_code'),
        url(r'^edit_phone/$', 'edit_phone', name='edit_phone'),
    )
