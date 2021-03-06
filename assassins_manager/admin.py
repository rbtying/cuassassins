from django.contrib import admin
from assassins_manager.models import Squad, Assassin, Contract, Game, KillReport
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import forms
from django.db.models.signals import post_save
from django.dispatch import receiver

class AssassinInline(admin.StackedInline):
    """ Inline admin class for Assassins in SquadAdmin """
    model = Assassin
    extra = 0

class SquadAdmin(admin.ModelAdmin):
    """ Admin class to handle squads """
    fieldsets = [
            (None, {'fields': ['game', 'name', 'code', 'public', 'alive', 'kills']}), 
            ]
    list_display = ('name', 'game', 'public',)
    inlines = [AssassinInline]

class AssassinAdmin(admin.ModelAdmin):
    """ Admin class to handle assassins """
    list_display = ('user', 'lifecode', 'alive', 'role', 'frozen')

admin.site.register(Assassin, AssassinAdmin)
admin.site.register(Squad, SquadAdmin)
admin.site.register(Game)
admin.site.register(Contract)
admin.site.register(KillReport)
