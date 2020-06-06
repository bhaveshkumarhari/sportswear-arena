from django.urls import path
from .views import HomeView, productList, createProduct, update_product, registerPage, loginPage, logoutUser, userPage

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', HomeView, name="dashboard-home"),
    path('dashboard/product-list', productList, name="dashboard-product-list"),
    path('dashboard/create-product/', createProduct.as_view(), name="create-product"),
    path('dashboard/update-product/<slug>/', update_product, name="update-product"),

    path('dashboard/register/', registerPage, name="dashboard-register"),
    path('dashboard/login/', loginPage, name="dashboard-login"),
    path('dashboard/logout/', logoutUser, name="dashboard-logout"),

    path('dashboard/user-page/', userPage.as_view(), name="user-page"),
]