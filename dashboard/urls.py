from django.urls import path
from .views import HomeView, registerPage, loginPage, userPage

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', HomeView, name="dashboard-home"),
    path('dashboard/register/', registerPage, name="dashboard-register"),
    path('dashboard/login/', loginPage, name="dashboard-login"),

    path('dashboard/user-page/', userPage.as_view(), name="user-page"),
]