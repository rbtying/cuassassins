from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views

urlpatterns = patterns('columbia_util.views',
        (r'^whoami/$', 'whoami'),
        (r'^register/$', 'register',),
    )

urlpatterns += patterns('',
        (r'^login/$', auth_views.login, {'template_name': 'user/login.html'}, 'login'),
        (r'^logout/$', auth_views.logout, {'template_name': 'user/logout.html'}, 'logout'),
        (r'^password/reset/$', auth_views.password_reset, {'template_name': 'user/passwordreset.html'}, 'password_reset'),
        (r'^password/reset/done/$', auth_views.password_reset_done, {'template_name': 'user/passwordreset.html'}),
        (r'^password/reset/confirm/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$', auth_views.password_reset_confirm, {'template_name': 'user/passwordconfirm.html'}),
        (r'^password/reset/complete/$', auth_views.password_reset_complete, {'template_name': 'user/passwordcomplete.html'}),
        (r'^password/change/$', auth_views.password_change, {'template_name': 'user/passwordchange.html'}, 'password_change'),
        (r'^password/change/done/$', auth_views.password_change_done, {'template_name': 'user/passwordchange.html'}),
    )

