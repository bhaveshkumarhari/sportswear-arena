from django.conf import settings
from django.db import models
from django.shortcuts import reverse

from django_countries.fields import CountryField

CATEGORY_CHOICES = (
    ('TP','Track Pants'),
    ('ET','Event T-Shirt'),
    ('CUT','Customized T-Shirt'),
    ('COT','Corporate T-Shirt'),
    ('GT','Graphics T-Shirt'),
    ('SPT','Sports T-Shirt'),
    ('SUT','Sublimation T-Shirt'),
    ('CT','Collar T-Shirt'),
    ('RNT','Round Neck T-Shirt')
)

ADDRESS_CHOICES = (
    ('B','Billing'),
    ('S','Shipping'),
)

class Category(models.Model):
    title = models.CharField(choices=CATEGORY_CHOICES, max_length=3)
    description = models.TextField(max_length=1000)
    image = models.CharField(max_length=100)
    # image = models.ImageField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Categories'

    def get_absolute_url(self):
        return reverse("core:product-list", kwargs={
            'title': self.title
        })

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=3)
    slug = models.SlugField()
    description = models.TextField()
    front_image = models.ImageField()
    back_image = models.ImageField()
    side_image = models.ImageField()
    quantity = models.IntegerField(default=1)
    new = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })
    
    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })
    
    def saving_price(self):
        return int(self.price - self.discount_price)

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    # calculate price with item quantity
    def get_total_item_price(self):
        return self.quantity * self.item.price

    # calculate discounted price with item quantity
    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    # calculate saving amount
    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total
    
    def get_total_quantity(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.quantity
        return total

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'

class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    subject = models.CharField(max_length=50)
    message = models.TextField(max_length=500)

    def __str__(self):
        return self.email

