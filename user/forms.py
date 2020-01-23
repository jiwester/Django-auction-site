from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from user.models import UserProfile
from django.forms import ModelForm


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {'password': forms.PasswordInput()}

    def clean_username(self):
        username = self.cleaned_data['username']
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("This username has been taken")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError("This email has been taken")
        return email

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class EditProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['password', 'email']
        widgets = {'password': forms.PasswordInput()}

    def clean_email(self):
        email = self.cleaned_data['email']
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError("This email has been taken")
        return email


class CreateAuctionForm(forms.Form):
    title = forms.CharField()
    description = forms.CharField()
    minimum_price = forms.FloatField()
    deadline_date = forms.DateTimeField(input_formats=['%d.%m.%Y %H:%M:%S'], help_text="(DD.MM.YYYY HH:mm:ss)")


class ConfirmAuction(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)


class EditAuctionForm(forms.Form):
    description = forms.CharField()


class SearchForm(forms.Form):
    search = forms.CharField(label="Search")


class BidForm(forms.Form):
    new_price = forms.FloatField()
