from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from models import *
# from models import ColumbiaUser
# from forms import ColumbiaUserCreationForm, ColumbiaUserChangeForm

# class ColumbiaUserAdmin(UserAdmin):
#     form = ColumbiaUserChangeForm
#     add_form = ColumbiaUserCreationForm
# 
#     list_display = ('email', 'is_staff',)
#     list_filter = ('is_staff',)
#     fieldsets = (
#             ('Login', {'fields': ('username', 'password', )}),
#             ('Permissions', {'fields': ('is_staff', 'is_active',)}),
#             ('LDAP information (do not edit, will be reset)', 
#                 {'fields': ('first_name', 'last_name',
#                 'email', 'address', 'mailbox', 'school')}),
#         )
# 
#     add_fieldsets = (
#             (None, { 'classes': ('wide',),
#                 'fields': ('username', 'password1', 'password2',)
#                 }
#             ),
#         )
#     search_fields = ('username',)
#     ordering = ('username',)
#     filter_horizontal = ()
# 
# admin.site.register(ColumbiaUser, ColumbiaUserAdmin)
admin.site.register(ColumbiaUserProfile)
admin.site.unregister(Group)
