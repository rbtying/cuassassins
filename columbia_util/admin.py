from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from models import *

class ColumbiaUserProfileAdmin(admin.ModelAdmin):
	def name(v):
		return v.user.get_full_name() or v.user.username
	list_display = (name, )
	pass

admin.site.register(ColumbiaUserProfile, ColumbiaUserProfileAdmin)
admin.site.unregister(Group)
