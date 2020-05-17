from django.urls import path
from .views import (
    HomeView, ProductListView, ProductDetailView, ContactView, add_to_cart, OrderSummaryView
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('product/<slug>/', ProductDetailView.as_view(), name="product"),
    path('product-list/<title>/', ProductListView, name="product-list"),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name="order-summary"),
    path('contact-us/', ContactView.as_view(), name="contact-us"),
]