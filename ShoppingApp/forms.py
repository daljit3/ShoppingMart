from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ShoppingApp.models import ShoppingList, ShoppingListItem, ShoppingListItemCategory


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=150)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email):
            raise ValidationError("This email address already exists!")
        return email


class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['name']


class ShoppingListItemForm(forms.ModelForm):
    # description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))
    quantity = forms.IntegerField(initial=1)
    # category = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # To get request.user
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ShoppingListItemCategory.objects.filter(
            user=self.user)

    class Meta:
        model = ShoppingListItem
        fields = ['name', 'quantity', 'category']


class ArchiveListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['archived']


class CompleteAListItemForm(forms.ModelForm):
    # completed = forms.BooleanField(required=False)
    class Meta:
        model = ShoppingListItem
        fields = ['completed']


class ShoppingListItemCategoryForm(forms.ModelForm):

    class Meta:
        model = ShoppingListItemCategory
        fields = ['name']
