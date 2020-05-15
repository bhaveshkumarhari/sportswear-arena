from django.urls import path
from .views import (
    HomeView, ProductListView, ProductDetailView, ContactView
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('product/<slug>/', ProductDetailView.as_view(), name="product"),
    path('product-list/', ProductListView.as_view(), name="product-list"),
    path('contact-us/', ContactView.as_view(), name="contact-us"),
]