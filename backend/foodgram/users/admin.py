from django.contrib import admin

from .models import User, Subscribers

admin.site.register(User)
admin.site.register(Subscribers)
