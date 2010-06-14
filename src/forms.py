from google.appengine.ext.db import djangoforms
from models import Account, Customer, Category

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
        #raise ValueError(dir(self.fields['parent_category']))
        self.fields['parent_category'].query = Category.all()\
            .filter('user =', user)\
            .filter('type =', type)\
            .filter('parent_category =', None)\
            .order('name')

    class Meta:
        model = Category
        exclude = ['user', 'type']
