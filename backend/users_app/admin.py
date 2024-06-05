from django.contrib import admin

from users_app.models import User


class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username',)


admin.site.register(User, UserAdmin)
