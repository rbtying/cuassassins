from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from django_facebook import registration_views
from django_facebook.utils import replication_safe

urlpatterns = patterns('columbia_util.views',
        (r'^whoami/$', 'whoami'),
    )

urlpatterns += patterns('',
        (r'^login/$', replication_safe(auth_views.login), {'template_name': 'reigstration/login.html'}, 'login'),
        (r'^logout/$', replication_safe(auth_views.logout), {'template_name': 'registration/logout.html'}, 'logout'),
        (r'^password/reset/$', auth_views.password_reset, {'template_name': 'registration/password_reset.html'}, 'password_reset'),
        (r'^password/reset/done/$', auth_views.password_reset_done, {'template_name': 'registration/password_reset.html'}),
        (r'^password/reset/confirm/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$', auth_views.password_reset_confirm, {'template_name': 'registration/confirm_password.html'}),
        (r'^password/reset/complete/$', auth_views.password_reset_complete, {'template_name': 'registration/password_reset_complete.html'}),
        (r'^password/change/$', auth_views.password_change, {'template_name': 'registration/change_password.html'}, 'password_change'),
        (r'^register/$', 'django_facebook.registration_views.register', 'register'),
        (r'^password/change/done/$', auth_views.password_change_done, {'template_name': 'registration/change_password.html'}),
    )

