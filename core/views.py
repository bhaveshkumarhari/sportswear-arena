from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, View, DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils import timezone

from django.contrib import messages

from .models import Item, Contact, Category, OrderItem, Order

from .forms import ContactForm

from django.core.paginator import Paginator

from .decorators import unauthenticated_user


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
            
        if self.request.user.is_staff:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context['cart'] = order

        return render(self.request, 'index.html', context)

    def post(self, *args, **kwargs):
        form = ContactForm(self.request.POST or None)
        print(self.request.POST)
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

    fitlered_items = Item.objects.filter(category=title)

    context = {'item_list': fitlered_items, 'count_all': count_all, 'count_round': count_round, 'count_collar': count_collar,
                   'count_track': count_track, 'count_customise': count_customise, 'count_corporate': count_corporate,'count_graphics': count_graphics,
                    'count_sports': count_sports, 'count_sublimation': count_sublimation, 'count_event': count_event}

    #---------------------------------------------------

    if request.user.is_staff:
            context['cart'] = Order.objects.get(user=request.user, ordered=False)

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


class ProductDetailView(DetailView):
    model = Item
    template_name = "product.html"
    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        context['item_list'] = Item.objects.all()
        if self.request.user.is_staff:
            context['cart'] = Order.objects.get(user=self.request.user, ordered=False)
        return context

@login_required
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

@login_required
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


@login_required
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