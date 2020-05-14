from django.db import models
from django.shortcuts import reverse

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

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.IntegerField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=3)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()
    quantity = models.IntegerField(default=1)
    new = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })
    
    def total_price(self):
        return self.price + self.discount_price

class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    image = models.CharField(max_length=100)
    # image = models.ImageField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Categories'

class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    subject = models.CharField(max_length=50)
    message = models.TextField(max_length=500)

    def __str__(self):
        return self.email

