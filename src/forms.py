# -*- coding: utf-8 -*-
from google.appengine.ext.db import djangoforms
from django import forms
from models import Account, Customer, Category, Transaction

class AccountForm(djangoforms.ModelForm):
    class Meta:
        model = Account
        exclude = ['user', 'slug', 'n_customers']

class CustomerForm(djangoforms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['account', 'slug']

class CategoryForm(djangoforms.ModelForm):
    def __init__(self, user, type, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['parent_category'].query = Category.all()\
            .filter('user =', user)\
            .filter('type =', type)\
            .filter('parent_category =', None)\
            .order('name')

    class Meta:
        model = Category
        exclude = ['user', 'type']


class ExpenseForm(djangoforms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        self.fields['account'].query = Account.all().filter('user =', user)
        self.fields['category'].query = Category.all()\
            .filter('user =', user)\
            .filter('type =', 'Custo')\
            .order('name')

    class Meta:
        model = Transaction
        exclude = ['user', 'customer']


class DateRangeForm(forms.Form):
    start = forms.DateField(label="início")
    end = forms.DateField(label="fim")