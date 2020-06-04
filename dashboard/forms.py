from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.forms import ModelForm
from core.models import Item

from django import forms

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

TSHIRT_SIZES = (
    ('B','S'),
    ('M','M'),
    ('L','L'),
    ('XL','XL'),
    ('XXL','XXL'),
)

class ProductForm(forms.Form):
    title = forms.CharField()
    category = forms.ChoiceField(choices=CATEGORY_CHOICES)
    description = forms.CharField()
    size = forms.ChoiceField(choices=TSHIRT_SIZES)
    slug = forms.CharField()
    price = forms.FloatField()
    discount_price = forms.FloatField()
    front_image = forms.ImageField()
    back_image = forms.ImageField()
    side_image = forms.ImageField()
    quantity = forms.IntegerField()
    new = forms.BooleanField(required=False)

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = '__all__'

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields= ['username','email','password1','password2']
