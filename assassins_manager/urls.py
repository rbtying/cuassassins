from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('assassins_manager.services',
        url(r'^cron/$', 'game_cron'),
    )
urlpatterns += patterns('assassins_manager.views',
        url(r'^info/$', 'about', name='about'),
    )
urlpatterns += patterns('assassins_manager.game.views',
        url(r'^(?P<game>.+)/details/$', 'details', name='game_details'),
        url(r'^(?P<game>.+)/join/$', 'join_game', name='game_join'),
        url(r'^(?P<game>.+)/leave/$', 'leave_game', name='game_leave'),
        url(r'^(?P<game>.+)/scoreboard/$', 'scoreboard', name='game_scoreboard'),
        url(r'^(?P<game>.+)/a/(?P<page_length>\d+)/$', 'assassins'),
        url(r'^(?P<game>.+)/a/$', 'assassins', name='game_assassins_list'),
        url(r'^(?P<game>.+)/p/$', 'police', name='game_police_list'),
        url(r'^(?P<game>.+)/d/$', 'disavowed', name='game_disavowed_list'),
        url(r'^(?P<game>.+)/s/$', 'squads', name='game_squads_list'),
        url(r'^(?P<game>.+)/c/$', 'contracts', name='game_contracts_list'),
        url(r'^(?P<game>.+)/admin/start_game/$', 'start_game', name='game_start'),
        url(r'^(?P<game>.+)/admin/end_game/$', 'end_game', name='game_end'),
        url(r'^(?P<game>.+)/admin/reset_game/$', 'reset_game', name='game_reset'),
        url(r'^(?P<game>.+)/admin/delete_game/$', 'delete_game', name='game_delete'),
        url(r'^(?P<game>.+)/admin/add_police/$', 'add_police', name='police_add'),
        url(r'^(?P<game>.+)/admin/remove_police/$', 'remove_police', name='police_remove'),
        url(r'^(?P<game>.+)/admin/$', 'game_admin', name='game_admin'),
        url(r'^create_game/$', 'create_game', name='game_create'),
        url(r'^$', 'gamelist', name='game_list'),
    )
urlpatterns += patterns('assassins_manager.squad.views',
        url(r'^(?P<game>.+)/s/details/(?P<squad>\d+)/$', 'details', name='squad_details'),
        url(r'^(?P<game>.+)/s/details/$', 'my_details', name='my_squad_details'),
        url(r'^(?P<game>.+)/s/contracts/$', 'my_contracts', name='my_contracts'),
        url(r'^(?P<game>.+)/s/add_squad/$', 'add_squad', name='squad_add'),
        url(r'^(?P<game>.+)/s/join_squad/$', 'join_squad', name='squad_join'),
        url(r'^(?P<game>.+)/s/leave_squad/$', 'leave_squad', name='squad_leave'),
    )
urlpatterns += patterns('assassins_manager.assassin.views',
        url(r'^(?P<game>.+)/a/details/(?P<username>.+)/$', 'details', name='assassin_details'),
        url(r'^(?P<game>.+)/a/details/$', 'my_details', name='my_details'),
    )
urlpatterns += patterns('assassins_manager.kill.views',
        url(r'^(?P<game>.+)/report_kill/$', 'report_kill', name='report_kill'),
        url(r'^(?P<game>.+)/report_kill_admin/$', 'report_kill_admin', name='report_kill_admin'),
        url(r'^report_kill_text/(?P<number>.+)/(?P<text>.+)/$', 'report_kill_text', name='report_kill_text'),
        url(r'^text/$', 'text', name='text'),
    )
urlpatterns += patterns('assassins_manager.contract.views',
        url(r'^(?P<game>.+)/c/details/(?P<contract>\d+)/$', 'details', name='contract_details'),
    )
urlpatterns += patterns('assassins_manager.report.views',
        url(r'^(?P<game>.+)/r/k/(?P<username>.+)/$', 'playerkills', name='player_kills'),
        url(r'^(?P<game>.+)/r/d/(?P<username>.+)/$', 'playerdeaths', name='player_deaths'),
        url(r'^(?P<game>.+)/r/(?P<report>\d+)/$', 'killreport', name='kill_report'),
        url(r'^(?P<game>.+)/r/$', 'killreports', name='game_kills'),
    )
