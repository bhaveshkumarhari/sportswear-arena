from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.generic import ListView, View, DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group

from django.utils import timezone

from django.contrib import messages

from .models import Item, Contact, Category, OrderItem, Order, Address, UserProfile, Payment

from .forms import ContactForm, ProductForm, CheckoutForm, CreateUserForm, UserInfoForm, PaymentForm, ShippingAddressForm, BillingAddressForm

from .decorators import unauthenticated_user

from django.conf import settings

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# from django.core.paginator import Paginator

# from django.views.generic.edit import FormMixin


# @unauthenticated_user
def registerPage(request):
    # if request.user.is_authenticated:
    #     return redirect('core:home')
    # else:
    form = CreateUserForm()
    # profile_form = UserProfileForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        # profile_form = UserProfileForm(request.POST)
        if form.is_valid():
            user = form.save()
            # profile_form.save()
            username = form.cleaned_data.get('username')

            # For every user registration, add user to customer group
            group = Group.objects.get(name='customer')
            user.groups.add(group)

            messages.success(request,'Account was created for ' + username)
            return redirect('core:login')

    context = {'form':form}
    return render(request, 'register.html', context)

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
            return redirect('core:home')
        else:
            messages.warning(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('/')

def userProfile(request):

    shippingform = ShippingAddressForm()

    billingform = BillingAddressForm()
    
    userform = UserInfoForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        if userform.is_valid():
            first_name = userform.cleaned_data.get('first_name')
            last_name = userform.cleaned_data.get('last_name')
            email = userform.cleaned_data.get('email')
            
            if is_valid_form([first_name, last_name, email]):
                userform.save()
                messages.success(request, "User information was changed successfully.")
                return redirect('core:user-profile')
    

    try:
        shipping_address = Address.objects.get(user=request.user, address_type='S', default=True)
    except ObjectDoesNotExist:
        shipping_address = False

    try:
        billing_address = Address.objects.get(user=request.user, address_type='B', default=True)
    except ObjectDoesNotExist:
        billing_address = False

    context = {'shipping_address':shipping_address, 'billing_address':billing_address, 'userform':userform, 'shippingform':shippingform, 'billingform':billingform}
    
    if request.user.is_authenticated:
        try:
            context['cart'] = Order.objects.get(user=request.user, ordered=False)
        except:
            ordered_date = timezone.now() # get current date
            context['cart'] = Order.objects.create(user=request.user, ordered_date=ordered_date)

    return render(request, 'user_profile.html', context)


def shippingAddress(request):

    if request.method == 'POST':
        
        form = ShippingAddressForm(request.POST or None)

        if form.is_valid():
            shipping_address = form.cleaned_data.get('shipping_address')
            shipping_address2 = form.cleaned_data.get('shipping_address2')
            shipping_country = form.cleaned_data.get('shipping_country')
            shipping_zip = form.cleaned_data.get('shipping_zip')
            shipping_state = form.cleaned_data.get('shipping_state')
            
            if is_valid_form([shipping_address, shipping_country, shipping_zip, shipping_state]):
                try:
                    old_shipping_address = Address.objects.get(user=request.user, address_type = 'S')
                    old_shipping_address.delete()
                except ObjectDoesNotExist:
                    pass
                shipping_address = Address(
                        user = request.user,
                        street_address = shipping_address,
                        apartment_address = shipping_address2,
                        country = shipping_country,
                        zip = shipping_zip,
                        state = shipping_state,
                        address_type = 'S',
                        default = True
                    )
                shipping_address.save()

                #---------- IF SAME BILLING ADDRESS CHECKED --------------

                same_billing_address = form.cleaned_data.get('same_billing_address')

                if same_billing_address:
                    try:
                        old_billing_address = Address.objects.get(user=request.user, address_type = 'B')
                        old_billing_address.delete()
                    except ObjectDoesNotExist:
                        pass
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    messages.success(request, "Billing address was changed successfully.")
                
                #-----------------------------------------------------------
                messages.success(request, "Shipping address was changed successfully.")
                return redirect('core:user-profile')


def billingAddress(request):

    if request.method == 'POST':
        
        form = BillingAddressForm(request.POST or None)

        if form.is_valid():
            billing_address = form.cleaned_data.get('billing_address')
            billing_address2 = form.cleaned_data.get('billing_address2')
            billing_country = form.cleaned_data.get('billing_country')
            billing_zip = form.cleaned_data.get('billing_zip')
            billing_state = form.cleaned_data.get('billing_state')
            
            if is_valid_form([billing_address, billing_country, billing_zip, billing_state]):
                try:
                    old_billing_address = Address.objects.get(user=request.user, address_type = 'B')
                    old_billing_address.delete()
                except ObjectDoesNotExist:
                    pass

                billing_address = Address(
                        user = request.user,
                        street_address = billing_address,
                        apartment_address = billing_address2,
                        country = billing_country,
                        zip = billing_zip,
                        state = billing_state,
                        address_type = 'B',
                        default = True
                    )
                billing_address.save()

                #-----IF SAME SHIPPING ADDRESS CHECKED ----------------------

                same_shipping_address = form.cleaned_data.get('same_shipping_address')

                if same_shipping_address:
                    try:
                        old_shipping_address = Address.objects.get(user=request.user, address_type = 'S')
                        old_shipping_address.delete()
                    except ObjectDoesNotExist:
                        pass
                    shipping_address = billing_address
                    shipping_address.pk = None
                    shipping_address.save()
                    shipping_address.address_type = 'S'
                    shipping_address.save()
                    messages.success(request, "Shipping address was changed successfully.")
                
                #-------------------------------------------------------------
                messages.success(request, "Billing address was changed successfully.")
                return redirect('core:user-profile')

class HomeView(View):

    def get(self, *args, **kwargs):

        categories = Category.objects.all()

        items = Item.objects.all()

        count_all = items.count()

        count_round = items.filter(category='RNT').count()
        count_collar = items.filter(category='CT').count()
        count_track = items.filter(category='TP').count()
        count_customise = items.filter(category='CUT').count()
        count_corporate = items.filter(category='COT').count()
        count_graphics = items.filter(category='GT').count()
        count_sports = items.filter(category='SPT').count()
        count_sublimation = items.filter(category='SUT').count()
        count_event = items.filter(category='ET').count()
        
        context = {'categories': categories, 'count_all': count_all, 'items': items, 'count_round': count_round, 'count_collar': count_collar,
                   'count_track': count_track, 'count_customise': count_customise, 'count_corporate': count_corporate,'count_graphics': count_graphics,
                    'count_sports': count_sports, 'count_sublimation': count_sublimation, 'count_event': count_event }
            
        if self.request.user.is_authenticated:
            try:
                context['cart'] = Order.objects.get(user=self.request.user, ordered=False)
            except:
                ordered_date = timezone.now() # get current date
                context['cart'] = Order.objects.create(user=self.request.user, ordered_date=ordered_date)

        return render(self.request, 'index.html', context)

    def post(self, *args, **kwargs):
        form = ContactForm(self.request.POST or None)
        # print(self.request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')

            contacts = Contact(
                name = name,
                email = email,
                subject = subject,
                message = message
            )
            contacts.save() 

            return redirect('/')


def ProductListView(request, title):

    items = Item.objects.all()

    count_all = items.count()

    count_round = items.filter(category='RNT').count()
    count_collar = items.filter(category='CT').count()
    count_track = items.filter(category='TP').count()
    count_customise = items.filter(category='CUT').count()
    count_corporate = items.filter(category='COT').count()
    count_graphics = items.filter(category='GT').count()
    count_sports = items.filter(category='SPT').count()
    count_sublimation = items.filter(category='SUT').count()
    count_event = items.filter(category='ET').count()

    #--------------------------------------------------

    filtered_items = Item.objects.filter(category=title)

    context = {'item_list': filtered_items, 'count_all': count_all, 'count_round': count_round, 'count_collar': count_collar,
                   'count_track': count_track, 'count_customise': count_customise, 'count_corporate': count_corporate,'count_graphics': count_graphics,
                    'count_sports': count_sports, 'count_sublimation': count_sublimation, 'count_event': count_event}

    #---------------------------------------------------

    if request.user.is_authenticated:
            try:
                context['cart'] = Order.objects.get(user=request.user, ordered=False)
            except:
                ordered_date = timezone.now() # get current date
                context['cart'] = Order.objects.create(user=request.user, ordered_date=ordered_date)

    if title == 'RNT':
        context['RNT'] = True
    if title == 'CT':
        context['CT'] = True
    if title == 'TP':
        context['TP'] = True
    if title == 'CUT':
        context['CUT'] = True
    if title == 'COT':
        context['COT'] = True
    if title == 'GT':
        context['GT'] = True
    if title == 'SPT':
        context['SPT'] = True
    if title == 'SUT':
        context['SUT'] = True
    if title == 'ET':
        context['ET'] = True

    return render(request, 'product-list.html', context)

class ProductDetailView(View):

    def get(self, *args, **kwargs):
        global slug_value
        slug_value = kwargs
        context = {}
        context['object'] = Item.objects.get(slug=slug_value['slug'])
        context['item_list'] = Item.objects.all()
        if self.request.user.is_authenticated:
            try:
                context['cart'] = Order.objects.get(user=self.request.user, ordered=False)
            except:
                ordered_date = timezone.now() # get current date
                context['cart'] = Order.objects.create(user=self.request.user, ordered_date=ordered_date)

        return render(self.request, 'product.html', context)
    
    def post(self, *args, **kwargs):
        print(self.request.POST)
        form = ProductForm(self.request.POST or None)
        if form.is_valid():
            value = form.cleaned_data.get('value')
            size = form.cleaned_data.get('size')
            color = form.cleaned_data.get('color')
        
        print(value)
        print(size)
        print(color)

        product_var = []
        product_var.append(size)
        product_var.append(color)
        print(product_var)

        item = get_object_or_404(Item, slug=slug_value['slug']) # get specific item with slug

        if self.request.user.is_authenticated:
            # If item is not in OrderItem model then add item else get the item
            order_item, created = OrderItem.objects.get_or_create(
                item=item,
                user=self.request.user,
                ordered=False
                )

            # filter Order model which is not ordered yet by the specific user
            order_qs = Order.objects.filter(user=self.request.user, ordered=False) 

            if order_qs.exists():
                order = order_qs[0] # grab the order from the order_qs
                
                # check if an item exists in Order model with slug
                if order.items.filter(item__slug=item.slug).exists():
                    
                    order_item.quantity = int(value)
                    order_item.save() # Save OrderItem model
                    messages.info(self.request, "This item quantity was updated.")
                    return redirect("core:order-summary")
                else:
                    # print(order_item)
                    order.items.add(order_item) # Add item to Order model if item does not exist in OrderItem.
                    # for item in product_var:
                    #     order_item.variations.add(item)
                    order_item.quantity = int(value)
                    order_item.save() # Save OrderItem model
                    messages.info(self.request, "This item was added to your cart.")
                    return redirect("core:order-summary")
            else:
                # print(order_item)
                ordered_date = timezone.now() # get current date
                order = Order.objects.create(user=self.request.user, ordered_date=ordered_date) # Create Order model instance with specific user and ordered date
                order.items.add(order_item) # Then add order_item to that model instance
                order_item.quantity = int(value)
                # for item in product_var:
                #         order_item.variations.add(item)
                # order_item.size = size
                order_item.save() # Save OrderItem model
                messages.info(self.request, "This item was added to your cart.")
                return redirect("core:order-summary")

        return redirect('core:order-summary')

@login_required(login_url='core:login')
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug) # get specific item with slug
    # If item is not in OrderItem model then add item else get the item
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
        )

    # filter Order model which is not ordered yet by the specific user
    order_qs = Order.objects.filter(user=request.user, ordered=False) 

    if order_qs.exists():
        order = order_qs[0] # grab the order from the order_qs

        # check if an item exists in Order model with slug
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1 # Increase quantity in OrderItem model if there is an item exists
            order_item.save() # Save OrderItem model
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item) # Add item to Order model if item does not exist in OrderItem.
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now() # get current date
        order = Order.objects.create(user=request.user, ordered_date=ordered_date) # Create Order model instance with specific user and ordered date
        order.items.add(order_item) # Then add order_item to that model instance
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")

@login_required(login_url='core:login')
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug) # get specific item with slug

    # filter Order model which is not ordered yet by the specific user
    order_qs = Order.objects.filter(
        user=request.user, 
        ordered=False
    ) 

    if order_qs.exists():
        order = order_qs[0] # grab the order from the order_qs

        # check if an item exists in Order model with slug
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item) # Remove item if an item exists in Order model
            #------if item quantity is more than 1 and removed item from cart, Set item quantity to 1 in OrderItem
            if order_item.quantity > 1:
                order_item.quantity = 1
                order_item.save() # Save OrderItem model
            #-------------------------------------
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("core:product",slug=slug)
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("core:product",slug=slug)


@login_required(login_url='core:login')
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug) # get specific item with slug

    # filter Order model which is not ordered yet by the specific user
    order_qs = Order.objects.filter(
        user=request.user, 
        ordered=False
    ) 

    if order_qs.exists():
        order = order_qs[0] # grab the order from the order_qs

        # check if an item exists in Order model with slug
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1 # Decrease quantity in OrderItem model if there is an item exists
                order_item.save() # Save OrderItem model
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("core:product",slug=slug)
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("core:product",slug=slug)


class OrderSummaryView(LoginRequiredMixin, View):
    login_url = 'core:login'
    redirect_field_name = 'core:order-summary'

    def get(self, *args, **kwargs):

        try:
            # get the items which are not ordered yet from current user
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'cart':order
            }
            return render(self.request, 'order_summary.html', context)
            
        except ObjectDoesNotExist:
            # if there is no active order then shows message
            messages.warning(self.request, "You do not have active order")
            return redirect("/")


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class CheckoutView(LoginRequiredMixin, View):
    login_url = 'core:login'
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                # 'couponform': CouponForm,
                'order': order,
                # 'DISPLAY_COUPON_FORM': True # Displays coupon form.
            }

            shipping_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type = 'S',
                default = True
            )

            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})


            billing_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type = 'B',
                default = True
            )

            if billing_address_qs.exists():
                context.update({'default_billing_address': billing_address_qs[0]})

            if self.request.user.is_authenticated:
                try:
                    context['cart'] = Order.objects.get(user=self.request.user, ordered=False)
                except:
                    ordered_date = timezone.now() # get current date
                    context['cart'] = Order.objects.create(user=self.request.user, ordered_date=ordered_date)
                    
            return render(self.request, 'checkout.html', context)
        
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")
    
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            # check if order is already exists and not yet completed.
            order = Order.objects.get(user=self.request.user, ordered=False)
            #print(self.request.POST) # printing the POST data to terminal
            if form.is_valid():

#---------------------------- FOR SHIPPING ADDRESS ----------------------------------------

                #------- If checkbox selected to use default shipping address --------
                use_default_shipping = form.cleaned_data.get('use_default_shipping')

                if use_default_shipping:
                    print("Using the default shipping address")
                    address_qs = Address.objects.filter(
                        user = self.request.user,
                        address_type = 'S',
                        default = True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()

                    else:
                        messages.info(self.request, "No default shipping address available")
                        return redirect('core:checkout')
                #----- Else user will enter new shipping address------------------------
                else:
                    print("User is entering a new shipping address")

                    # Get the cleaned data from the form.
                    shipping_address = form.cleaned_data.get('shipping_address')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    shipping_state = form.cleaned_data.get('shipping_state')


                    # functionality is above
                    if is_valid_form([shipping_address, shipping_country, shipping_zip, shipping_state]):
                        # Assign the data to BillingAddress model fields
                        shipping_address = Address(
                            user = self.request.user,
                            street_address = shipping_address,
                            apartment_address = shipping_address2,
                            country = shipping_country,
                            zip = shipping_zip,
                            state = shipping_state,
                            address_type = 'S'
                        )
                        shipping_address.save() # Save the assigned data
                        order.shipping_address = shipping_address
                        order.save()

                        #------- If checkbox selected to set default shipping address --------
                        set_default_shipping = form.cleaned_data.get('set_default_shipping')

                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                        #---------------------------------------------------------------------
                    else:
                        messages.info(self.request, "Please fill in the required shipping address fields")

#---------------------------- FOR BILLING ADDRESS ----------------------------------------

                #------- If checkbox selected to use default shipping address --------
                use_default_billing = form.cleaned_data.get('use_default_billing')
                #------- If checkbox selected to use same billing address as shipping address-
                same_billing_address = form.cleaned_data.get('same_billing_address')

                #------- If checkbox selected to use same billing address as shipping address-
                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                #------- elif checkbox selected to use default shipping address --------
                elif use_default_billing:
                    print("Using the default billing address")
                    address_qs = Address.objects.filter(
                        user = self.request.user,
                        address_type = 'B',
                        default = True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "No default billing address available")
                        return redirect('core:checkout')
                #----- Else user will enter new billing address------------------------
                else:
                    print("User is entering a new billing address")

                    billing_address1 = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')
                    billing_state = form.cleaned_data.get('billing_state')
                    
                    if is_valid_form([billing_address1, billing_country, billing_zip, billing_state]):
                        # Assign the data to Address model fields
                        billing_address = Address(
                            user = self.request.user,
                            street_address = billing_address1,
                            apartment_address = billing_address2,
                            country = billing_country,
                            zip = billing_zip,
                            state = billing_state,
                            address_type = 'B'
                        )
                        billing_address.save() # Save the assigned data

                        order.billing_address = billing_address
                        order.save()

                        #------- If checkbox selected to set default shipping address --------
                        set_default_billing = form.cleaned_data.get('set_default_billing')

                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                        #---------------------------------------------------------------------
                    else:
                        messages.info(self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'S':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    # Prints when data is invalid
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect('core:checkout')

        except ObjectDoesNotExist:
            # if there is no active order then shows message
            messages.error(self.request, "You do not have active order")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                # 'DISPLAY_COUPON_FORM': False # Does not display coupon form.
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, 'payment.html', context)
        else:
            messages.warning(self.request, "You have not added a billing address")
            return redirect("core:checkout")
    
    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        # token = self.request.POST.get('stripeToken') # get from stripeTokenHandler in payment.html
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        # print(self.request.POST)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="gbp",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="gbp",
                        source=token
                    )
                
                # Create the payment
                payment = Payment()
                # Assign the values to Payment model fields
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                
                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                # Assign the payment to the order

                order.ordered = True # When order is completed
                order.payment = payment
                # order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful")
                return redirect("core:customer-orders")

            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                body = e.json_body
                err = body.get('error',{})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(self.request, "A serious error occured. We have been notified. Error in Code.")
                return redirect("/")
            

class CustomerOrders(View):
    def get(self, *args, **kwargs):

        orders = Order.objects.filter(user=self.request.user, ordered = True)

        context = {'orders': orders}

        if self.request.user.is_authenticated:
            try:
                context['cart'] = Order.objects.get(user=self.request.user, ordered=False)
            except:
                ordered_date = timezone.now() # get current date
                context['cart'] = Order.objects.create(user=self.request.user, ordered_date=ordered_date)

        return render(self.request, 'customer_orders.html', context)

class ContactView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'contact.html')

    def post(self, *args, **kwargs):
        form = ContactForm(self.request.POST or None)
        # print(self.request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')

            contacts = Contact(
                name = name,
                email = email,
                subject = subject,
                message = message
            )
            contacts.save() 

            return redirect('/')