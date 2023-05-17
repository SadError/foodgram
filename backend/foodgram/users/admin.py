from django.contrib import admin

from .models import User, Subscribers


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    list_filter = ('email', 'first_name')


admin.site.register(User, UserAdmin)
admin.site.register(Subscribers)
