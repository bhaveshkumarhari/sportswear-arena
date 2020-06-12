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

from .models import Item, Contact, Category, OrderItem, Order, Address

from .forms import ContactForm, ProductForm, CheckoutForm, CreateUserForm, UserInfoForm, ShippingAddressForm, BillingAddressForm

from .decorators import unauthenticated_user

# from django.core.paginator import Paginator

# from django.views.generic.edit import FormMixin


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
            # phone_number = form.cleaned_data.get('phone_number')
            # print(phone_number)

            # phone = User(
            #     phone_number = phone_number,
            # )
            # phone.save() 

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
                return redirect('core:user-profile')

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
                return redirect('core:user-profile')
    
    userform = UserInfoForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        if userform.is_valid():
            first_name = userform.cleaned_data.get('first_name')
            last_name = userform.cleaned_data.get('last_name')
            email = userform.cleaned_data.get('email')
            
            if is_valid_form([first_name, last_name, email]):
                userform.save()
                return redirect('core:user-profile')
    

    try:
        shipping_address = Address.objects.get(user=request.user, address_type='S', default=True)
    except ObjectDoesNotExist:
        shipping_address = False

    try:
        billing_address = Address.objects.get(user=request.user, address_type='B', default=True)
    except ObjectDoesNotExist:
        billing_address = False

    context = {'shipping_address':shipping_address, 'billing_address':billing_address, 'userform':userform}
    
    return render(request, 'user_profile.html', context)


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
        
        form = ProductForm(self.request.POST or None)
        if form.is_valid():
            value = form.cleaned_data.get('value')
            size = form.cleaned_data.get('size')

        
        item = get_object_or_404(Item, slug=slug_value['slug']) # get specific item with slug
        # print(item)

        if self.request.user.is_authenticated:
            # If item is not in OrderItem model then add item else get the item
            order_item, created = OrderItem.objects.get_or_create(
                item=item,
                # size=size,
                user=self.request.user,
                ordered=False
                )
            # print(order_item)

            # filter Order model which is not ordered yet by the specific user
            order_qs = Order.objects.filter(user=self.request.user, ordered=False) 

            if order_qs.exists():
                order = order_qs[0] # grab the order from the order_qs
                
                # check if an item exists in Order model with slug
                if order.items.filter(item__slug=item.slug).exists():
                    
                    order_item.quantity += int(value) # Increase quantity in OrderItem model if there is an item exists
                    # order_item.size = size
                    order_item.save() # Save OrderItem model
                    messages.info(self.request, "This item quantity was updated.")
                    return redirect("core:order-summary")
                else:
                    # print(order_item)
                    order.items.add(order_item) # Add item to Order model if item does not exist in OrderItem.
                    order_item.quantity = int(value)
                    # order_item.size = size
                    order_item.save() # Save OrderItem model
                    messages.info(self.request, "This item was added to your cart.")
                    return redirect("core:order-summary")
            else:
                # print(order_item)
                ordered_date = timezone.now() # get current date
                order = Order.objects.create(user=self.request.user, ordered_date=ordered_date) # Create Order model instance with specific user and ordered date
                order.items.add(order_item) # Then add order_item to that model instance
                order_item.quantity = int(value)
                # order_item.size = size
                order_item.save() # Save OrderItem model
                messages.info(self.request, "This item was added to your cart.")
                return redirect("core:order-summary")

        return redirect('core:order-summary')

# class ProductDetailView(DetailView):
#     model = Item
#     template_name = "product.html"

#     def get_context_data(self, *args, **kwargs):
#         context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
#         context['item_list'] = Item.objects.all()
#         if self.request.user.is_staff: #TODO
#             context['cart'] = Order.objects.get(user=self.request.user, ordered=False)
#         return context

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

                return redirect('core:checkout')
                # if payment_option == 'S':
                #     return redirect('core:payment', payment_option='stripe')
                # elif payment_option == 'S':
                #     return redirect('core:payment', payment_option='paypal')
                # else:
                #     # Prints when data is invalid
                #     messages.warning(self.request, "Invalid payment option selected")
                #     return redirect('core:checkout')

        except ObjectDoesNotExist:
            # if there is no active order then shows message
            messages.error(self.request, "You do not have active order")
            return redirect("core:order-summary")
            

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