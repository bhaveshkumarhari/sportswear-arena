from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal')
)

class CreateUserForm(UserCreationForm):
    phone_number = forms.IntegerField(required=True)

    class Meta:
        model = User
        fields= ['first_name','last_name','username','email','password1','password2']

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.phone_number = self.cleaned_data['phone_number']

        if commit:
            user.save()

        return user


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='select country').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'ps-select selectpicker',
    }))
    shipping_zip = forms.CharField(required=False)
    shipping_state = forms.CharField(required=False)

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'ps-select selectpicker',
    }))
    billing_zip = forms.CharField(required=False)
    billing_state = forms.CharField(required=False)

    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)

    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))

class ProductForm(forms.Form):
    size = forms.CharField()
    value = forms.CharField()