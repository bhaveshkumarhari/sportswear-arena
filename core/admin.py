from django.contrib import admin
from .models import Item, OrderItem, Order, Contact, Category, Address

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(Address)
admin.site.register(Contact)
