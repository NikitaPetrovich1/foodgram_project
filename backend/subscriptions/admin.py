from django.contrib import admin
from .models import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author'
    )
    list_filter = ('user', 'author')
    search_fields = ('user__username', 'user__email')


admin.site.register(Subscription, SubscriptionAdmin)
