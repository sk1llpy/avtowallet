from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

if admin.site.is_registered(User):
    admin.site.unregister(User)
admin.site.unregister(Group)
