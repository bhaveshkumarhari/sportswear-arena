from django.shortcuts import render, redirect
from django.views.generic import View

from .forms import CreateUserForm, ItemForm, ProductForm

from django.contrib import messages

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group

from core.models import Item

from django.contrib.auth.models import User

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

def customerList(request):
    users = User.objects.all()
    context = {'users':users}
    return render(request, 'customer_list.html', context)

class createProduct(View):

    def get(self, *args, **kwargs):
        form = ProductForm()
        context = {'form':form}
        return render(self.request, 'create_product.html', context)
    def post(self, *args, **kwargs):
        form = ProductForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            category = form.cleaned_data.get('category')
            description = form.cleaned_data.get('description')
            size = form.cleaned_data.get('size')
            slug = form.cleaned_data.get('slug')
            quantity = form.cleaned_data.get('quantity')
            price = form.cleaned_data.get('price')
            discount_price = form.cleaned_data.get('discount_price')
            front_image = form.cleaned_data.get('front_image')
            back_image = form.cleaned_data.get('back_image')
            side_image = form.cleaned_data.get('side_image')
            new = form.cleaned_data.get('new')
            # print(discount_price)

            items = Item(
                title = title,
                category = category,
                description = description,
                size = size,
                slug = slug,
                quantity = quantity,
                price = price,
                discount_price = discount_price,
                front_image = front_image,
                back_image = back_image,
                side_image = side_image,
                new = new
            )
            items.save() 
            messages.success(self.request,'Successfully added product to your inventory')
            return redirect('dashboard:dashboard-product-list')
        messages.warning(self.request,'Please enter valid information')
        return redirect('dashboard:create-product')

def update_product(request, slug):
    try:
        product = Item.objects.get(slug=slug)
    except Item.DoesNotExist:
        return redirect('dashboard:dashboard-product-list')

    form = ItemForm(request.POST or None, instance = product)

    if form.is_valid():
        form.save()
        messages.success(request,'Successfully updated product of inventory')
        return redirect('dashboard:dashboard-product-list')
    print(product)
    context = {'form':form, 'product':product}
    return render(request, 'update_product.html', context)


def delete_product(request, slug):
    try:
        product = Item.objects.get(slug=slug)
    except Item.DoesNotExist:
        return redirect('dashboard:dashboard-product-list')

    product.delete()
    messages.warning(request,'Successfully deleted product from inventory')
    return redirect('dashboard:dashboard-product-list')


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