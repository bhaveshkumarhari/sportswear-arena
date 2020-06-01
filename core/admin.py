from django.contrib import admin
from .models import Item, OrderItem, Order, Contact, Category, Address

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    # 'being_delivered',
                    # 'received',
                    # 'refund_requested',
                    # 'refund_granted',
                    'shipping_address',
                    'billing_address',
                    # 'payment',
                    # 'coupon'
    ]
    list_display_links = [
                    'user',
                    'shipping_address',
                    'billing_address',
                    # 'payment',
                    # 'coupon'
    ]
    
    # list_filter = ['ordered',
                    # 'being_delivered',
                    # 'received',
                    # 'refund_requested',
                    # 'refund_granted'
                    # ]
    search_fields = [
        'user__username',
        # 'ref_code'
    ]
    # actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'state',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Category)
admin.site.register(Address, AddressAdmin)
admin.site.register(Contact)
