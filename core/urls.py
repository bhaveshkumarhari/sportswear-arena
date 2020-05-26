from django.urls import path
from .views import (
    HomeView, 
    ProductListView, 
    ProductDetailView, 
    ContactView, 
    add_to_cart, 
    remove_from_cart, 
    remove_single_item_from_cart, 
    OrderSummaryView,
    CheckoutView
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('product/<slug>/', ProductDetailView.as_view(), name="product"),
    path('product-list/<title>/', ProductListView, name="product-list"),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name="order-summary"),
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path('contact-us/', ContactView.as_view(), name="contact-us"),
]