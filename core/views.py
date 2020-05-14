from django.shortcuts import render, redirect
from django.views.generic import ListView, View, DetailView

from .models import Item, Contact, Category

from .forms import ContactForm


class HomeView(View):
    def get(self, *args, **kwargs):
        categories = Category.objects.all()

        items = Item.objects.all()

        count_all = items.count()

        count_round = items.filter(category='RNT').count()
        count_collar = items.filter(category='CT').count()
        
        context = {'categories': categories, 'count_all': count_all, 'items': items, 'count_round': count_round, 'count_collar': count_collar}

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

class ProductDetailView(DetailView):
    model = Item
    template_name = "product.html"
    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        context['item_list'] = Item.objects.all()
        return context

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