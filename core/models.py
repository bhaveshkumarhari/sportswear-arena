from django.db import models

# Create your models here.

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    image = models.ImageField()

    def __str__(self):
        return self.title

class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    subject = models.CharField(max_length=50)
    message = models.TextField(max_length=500)

    def __str__(self):
        return self.email

class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    image = models.ImageField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Categories'