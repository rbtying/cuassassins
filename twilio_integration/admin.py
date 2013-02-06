from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from models import PhoneNumber

admin.site.register(PhoneNumber)
