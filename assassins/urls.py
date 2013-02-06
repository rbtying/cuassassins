from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

from assassins_manager import urls

urlpatterns = patterns('',
    # url(r'^assassins/', include(urls)),
    # Examples:
    # url(r'^$', 'assassins.views.home', name='home'),
    # url(r'^assassins/', include('assassins.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^accounts/', include('columbia_util.urls')),
    url(r'^accounts/', include('django_facebook.auth_urls')),
    url(r'^phone/', include('twilio_integration.urls')),
    url(r'^', include('assassins_manager.urls')),
)
