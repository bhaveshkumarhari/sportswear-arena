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

# class ProductListView(ListView):
    # model = Item
    # paginate_by = 10
    # template_name = "product-list.html"

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