from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View

from django.core.exceptions import ObjectDoesNotExist

from .forms import CreateUserForm, ItemForm, ProductForm, ShippingAddressForm, BillingAddressForm, UserInfoForm

from django.contrib import messages

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group

from core.models import Item, Address

from django.contrib.auth.models import User

from django.contrib.auth.mixins import LoginRequiredMixin


@login_required(login_url='dashboard:dashboard-login')
# @allowed_users(allowed_roles=['admin'])
@admin_only
def HomeView(request):
    return render(request, 'dashboard.html')

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

@login_required(login_url='dashboard:dashboard-login')
@admin_only
def customerProfile(request, user):

    user = User.objects.get(username=user)

    if request.method == 'POST':
        
        form = ShippingAddressForm(request.POST or None)

        if form.is_valid():
            shipping_address = form.cleaned_data.get('shipping_address')
            shipping_address2 = form.cleaned_data.get('shipping_address2')
            shipping_country = form.cleaned_data.get('shipping_country')
            shipping_zip = form.cleaned_data.get('shipping_zip')
            shipping_state = form.cleaned_data.get('shipping_state')
            
            if is_valid_form([shipping_address, shipping_country, shipping_zip, shipping_state]):
                old_shipping_address = Address.objects.get(user=user, address_type = 'S')
                old_shipping_address.delete()
                shipping_address = Address(
                        user = user,
                        street_address = shipping_address,
                        apartment_address = shipping_address2,
                        country = shipping_country,
                        zip = shipping_zip,
                        state = shipping_state,
                        address_type = 'S',
                        default = True
                    )
                shipping_address.save()
                return redirect('dashboard:customer-profile', user=user)

    if request.method == 'POST':
        
        form = BillingAddressForm(request.POST or None)

        if form.is_valid():
            billing_address = form.cleaned_data.get('billing_address')
            billing_address2 = form.cleaned_data.get('billing_address2')
            billing_country = form.cleaned_data.get('billing_country')
            billing_zip = form.cleaned_data.get('billing_zip')
            billing_state = form.cleaned_data.get('billing_state')
            
            if is_valid_form([billing_address, billing_country, billing_zip, billing_state]):
                old_billing_address = Address.objects.get(user=user, address_type = 'B')
                old_billing_address.delete()
                billing_address = Address(
                        user = user,
                        street_address = billing_address,
                        apartment_address = billing_address2,
                        country = billing_country,
                        zip = billing_zip,
                        state = billing_state,
                        address_type = 'B',
                        default = True
                    )
                billing_address.save()
                return redirect('dashboard:customer-profile', user=user)
    
    userform = UserInfoForm(request.POST or None, instance=user)

    if request.method == 'POST':
        if userform.is_valid():
            first_name = userform.cleaned_data.get('first_name')
            last_name = userform.cleaned_data.get('last_name')
            email = userform.cleaned_data.get('email')
            
            if is_valid_form([first_name, last_name, email]):
                userform.save()
                return redirect('dashboard:customer-profile', user=user)

    try:
        shipping_address = Address.objects.get(user=user, address_type='S', default=True)
    except ObjectDoesNotExist:
        shipping_address = False

    try:
        billing_address = Address.objects.get(user=user, address_type='B', default=True)
    except ObjectDoesNotExist:
        billing_address = False

    context = {'user':user, 'shipping_address':shipping_address, 'billing_address':billing_address, 'form':userform}

    return render(request, 'dashboard_user_profile.html', context)


@login_required(login_url='dashboard:dashboard-login')
@admin_only
def productList(request):
    items = Item.objects.all()
    context = {'items':items}
    return render(request, 'dashboard_product_list.html', context)

@login_required(login_url='dashboard:dashboard-login')
@admin_only
def customerList(request):
    users = User.objects.filter(groups__name='customer')
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

@login_required(login_url='dashboard:dashboard-login')
@admin_only
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

    context = {'form':form, 'product':product}
    return render(request, 'update_product.html', context)

@login_required(login_url='dashboard:dashboard-login')
@admin_only
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


# def updateShippingAddress(request):

#     return render(request, 'update_product.html', context)


class userPage(View):

    def get(self, *args, **kwargs):

        return render(self.request, 'user_page.html')