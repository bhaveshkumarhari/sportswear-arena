from django.shortcuts import render, redirect
from django.views.generic import ListView, View

from .models import Item, Contact, Category

from .forms import ContactForm

# class HomeView(ListView):
#     model = Category
#     paginate_by = 4
#     template_name = "index.html"

class HomeView(View):
    def get(self, *args, **kwargs):
        categories = Category.objects.all()

        items = Item.objects.all()

        count_round = items.filter(category='RNT').count()
        count_collar = items.filter(category='CT').count()

        # print(count_collar)

        # for item in items:
        #     print(item.category)
        
        context = {'categories': categories, 'items': items, 'count_round': count_round, 'count_collar': count_collar}

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

            return redirect('home')


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