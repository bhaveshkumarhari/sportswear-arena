from django.urls import path
from .views import HomeView, productList, createProduct, update_product, delete_product, registerPage, loginPage, logoutUser, userPage, customerList

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', HomeView, name="dashboard-home"),
    path('dashboard/product-list', productList, name="dashboard-product-list"),
    path('dashboard/create-product/', createProduct.as_view(), name="create-product"),
    path('dashboard/update-product/<slug>/', update_product, name="update-product"),
    path('dashboard/delete-product/<slug>/', delete_product, name="delete-product"),

    path('dashboard/customer-list', customerList, name="customer-list"),

    path('dashboard/register/', registerPage, name="dashboard-register"),
    path('dashboard/login/', loginPage, name="dashboard-login"),
    path('dashboard/logout/', logoutUser, name="dashboard-logout"),

    path('dashboard/user-page/', userPage.as_view(), name="user-page"),
]