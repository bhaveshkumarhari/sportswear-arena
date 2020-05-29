from django.shortcuts import render, redirect
from django.views.generic import View

from .forms import CreateUserForm

from django.contrib import messages

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group

from core.models import Item

from django.contrib.auth.mixins import LoginRequiredMixin

@login_required(login_url='dashboard:dashboard-login')
# @allowed_users(allowed_roles=['admin'])
@admin_only
def HomeView(request):
    return render(request, 'dashboard.html')


@login_required(login_url='dashboard:dashboard-login')
@admin_only
def productList(request):
    items = Item.objects.all()
    context = {'items':items}
    return render(request, 'dashboard_product_list.html', context)


@unauthenticated_user
def registerPage(request):
    # if request.user.is_authenticated:
    #     return redirect('core:home')
    # else:
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # For every user registration, add user to customer group
            group = Group.objects.get(name='customer')
            user.groups.add(group)

            messages.success(request,'Account was created for ' + username)
            return redirect('dashboard:dashboard-login')
    context = {'form':form}
    return render(request, 'dashboard_register.html', context)

@unauthenticated_user
def loginPage(request):
    # if request.user.is_authenticated:
    #     return redirect('core:home')
    # else:
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard:dashboard-home')
        else:
            messages.warning(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'dashboard_login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('dashboard:dashboard-login')

class userPage(View):

    def get(self, *args, **kwargs):

        return render(self.request, 'user_page.html')