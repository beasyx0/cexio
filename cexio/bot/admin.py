from django.contrib import admin

from cexio.bot.models import BotConfigurationVariables, Order


@admin.register(BotConfigurationVariables)
class BotConfigurationVariablesAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('name', 'public_id', 'date', 'bot_on',
                    'pair', 'buy', 'upswing_buy', 'sell', 'downswing_sell',
                    'fee', 'auto_cancel_order_period',)
    list_filter = ('name',)
    search_fields = ['name', 'date']
    readonly_fields = ('date', 'public_id',)
    fieldsets = (
            (None, {
                'fields': ('public_id', 'date', 'name', 'bot_on',
                'pair', 'buy', 'upswing_buy', 'sell', 'downswing_sell',
                'fee', 'auto_cancel_order_period',
                ),
            }),
        )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'order_id', 'pair', 'order_type', 'price', 'amount', 'total',)
    list_filter = ('order_type', 'pair',)
    search_fields = ['date', 'order_id', ]
    readonly_fields = ('date', 'public_id', 'total',)
    fieldsets = (
            (None, {
                'fields': ('public_id', 'date', 'order_id', 'pair',
                'order_type', 'price', 'amount', 'total',),
            }),
        )


admin.site.site_title = "Crypto Bot"
admin.site.site_header = "Crypto Bot Admin"
admin.site.index_title = ""
admin.site.enable_nav_sidebar = False
