# -*- coding: utf-8 -*-
import os

from google.appengine.dist import use_library
use_library('django', '1.1')

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from forms import AccountForm, CustomerForm, CategoryForm, ExpenseForm
from models import Account, Customer, Category, Transaction

class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
            self.response.out.write(template.render(path, {
                'user': user,
                'logout_url': users.create_logout_url("/")
            }))
        else:
            self.redirect(users.create_login_url('/'))


class Accounts(webapp.RequestHandler):
    def _handler(self, post=False):
        user = users.get_current_user()
        if user:
            accounts = Account.all().filter('user =', user).order('name').run()

            if post:
                form = AccountForm(data=self.request.POST)
                if form.is_valid():
                    # Save the data, and redirect to the view page
                    entity = form.save(commit=False)
                    entity.user = user
                    entity.put()
                    self.redirect(self.request.uri)
                    return
            else:
                form = AccountForm()

            path = os.path.join(os.path.dirname(__file__), 'templates/accounts.html')
            self.response.out.write(template.render(path, {
                'accounts': accounts,
                'form': form,
                'user': user,
                'logout_url': users.create_logout_url("/")
            }))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def get(self):
        self._handler()

    def post(self):
        self._handler(True)


class AccountDetails(webapp.RequestHandler):
    def get(self, account_slug):
        user = users.get_current_user()
        if user:
            account = Account.all()\
                .filter('user =', user).filter('slug =', account_slug).get()

            customers = Customer.all().filter('account =', account).order('name').run()

            path = os.path.join(os.path.dirname(__file__), 'templates/account_details.html')
            self.response.out.write(template.render(path, {
                'account': account,
                'customers': customers,
                'user': user,
                'logout_url': users.create_logout_url("/")
            }))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class CustomerNew(webapp.RequestHandler):
    def _handler(self, account_slug, post=False):
        user = users.get_current_user()
        if user:

            account = Account.all()\
                .filter('user =', user).filter('slug =', account_slug).get()

            customers = Customer.all().filter('account =', account)

            if post:
                form = CustomerForm(data=self.request.POST)
                if form.is_valid():
                    # Save the data, and redirect to the view page
                    entity = form.save(commit=False)
                    entity.account = account
                    entity.put()
                    account.n_customers += 1
                    account.put()
                    self.redirect(account.get_absolute_url())
            else:
                form = CustomerForm()

            path = os.path.join(os.path.dirname(__file__), 'templates/customer_new.html')
            self.response.out.write(template.render(path, {
                'account': account,
                'customers': customers,
                'form': form,
                'user': user,
                'logout_url': users.create_logout_url("/")
            }))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def get(self, account_slug):
        self._handler(account_slug)

    def post(self, account_slug):
        self._handler(account_slug, post=True)

class CustomerDetails(webapp.RequestHandler):
    def _handler(self, account_slug, customer_slug, post=False):
        user = users.get_current_user()
        if user:
            account = Account.all()\
                .filter('user =', user).filter('slug =', account_slug).get()

            customer = Customer.all()\
                .filter('account =', account).filter('slug =', customer_slug).get()

            if post:
                form = CustomerForm(instance=customer, data=self.request.POST)
                if form.is_valid():
                    # Save the data, and redirect to the view page
                    form.save()
                    self.redirect(account.get_absolute_url())
            else:
                form = CustomerForm(instance=customer)

            path = os.path.join(os.path.dirname(__file__), 'templates/customer_details.html')
            self.response.out.write(template.render(path, {
                'account': account,
                'customer': customer,
                'form': form,
                'user': user,
                'logout_url': users.create_logout_url("/")
            }))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def get(self, account_slug, customer_slug):
        self._handler(account_slug, customer_slug)

    def post(self, account_slug, customer_slug):
        self._handler(account_slug, customer_slug, post=True)

class CustomerDelete(webapp.RequestHandler):
    def get(self, account_slug, customer_slug):
        user = users.get_current_user()
        if user:
            account = Account.all()\
                .filter('user =', user).filter('slug =', account_slug).get()

            customer = Customer.all()\
                .filter('account =', account).filter('slug =', customer_slug).get()

            account.n_customers -= 1
            account.put()
            customer.delete()
            self.redirect(account.get_absolute_url())
        else:
            self.redirect(users.create_login_url(self.request.uri))


class Categories(webapp.RequestHandler):
    def _handler(self, type, post=False):
        user = users.get_current_user()

        #cap first because of existing choices
        type = type[0].upper() + type[1:]

        if user:
            if post:
                form = CategoryForm(user, type, data=self.request.POST)
                if form.is_valid():
                    # Save the data, and redirect to the view page
                    category = form.save(commit=False)
                    category.user = user
                    category.type = type
                    category.put()
                    self.redirect(self.request.uri)
            else:
                form = CategoryForm(user, type)

            categories = Category.all()\
                .filter('user =', user)\
                .filter('type =', type)\
                .order('parent_category')\
                .order('name').run()

            categories_dict = {}
            for category in categories:
                parent_category_key = Category.parent_category.get_value_for_datastore(category)
                if parent_category_key is None:
                    categories_dict[category.key()] = {'name': category.name,
                                                      'childs': {}}
                else:
                    parent = categories_dict[parent_category_key]['childs']
                    parent[category.key()] = {'name': category.name}

            path = os.path.join(os.path.dirname(__file__), 'templates/categories.html')
            self.response.out.write(template.render(path, {
                'categories': categories_dict,
                'type': type,
                'form': form,
                'user': user,
                'logout_url': users.create_logout_url("/")
            }))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def get(self, type=None):
        self._handler(type)

    def post(self, type=None):
        self._handler(type, post=True)


class Expenses(webapp.RequestHandler):
    def _handler(self, post=False):
        user = users.get_current_user()
        if user:
            if post:
                form = ExpenseForm(user, data=self.request.POST)
                if form.is_valid():
                    transaction = form.save(commit=False)
                    transaction.user = user
                    transaction.put()
                    self.redirect(self.request.uri)
            else:
                form = ExpenseForm(user)

            expenses = Transaction.all().filter('user =', user)
            path = os.path.join(os.path.dirname(__file__), 'templates/expenses.html')
            self.response.out.write(template.render(path, {
                'expenses': expenses,
                'form': form,
                'user': user,
                'logout_url': users.create_logout_url("/")
            }))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def get(self):
        self._handler()

    def post(self):
        self._handler(post=True)


class Expense(webapp.RequestHandler):
    def _handler(self, expense_key, post=False):
        user = users.get_current_user()

        if user:
            instance = Transaction.get(expense_key)
            if post:
                form = ExpenseForm(user, instance=instance, data=self.request.POST)
                if form.is_valid():
                    form.save()
                    self.redirect("/despesas/")

            form = ExpenseForm(user, instance=instance)
            path = os.path.join(os.path.dirname(__file__), 'templates/expense.html')
            self.response.out.write(template.render(path, {
                'form': form,
                'user': user,
                'logout_url': users.create_logout_url("/")
            }))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def get(self, expense_key):
        self._handler(expense_key)

    def post(self, expense_key):
        self._handler(expense_key, post=True)


class ExpenseDelete(webapp.RequestHandler):
    def get(self, expense_key):
        user = users.get_current_user()

        if user:
            instance = Transaction.get(expense_key)
            instance.delete()
            self.redirect("/despesas/")
        else:
            self.redirect(users.create_login_url(self.request.uri))


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/contas/', Accounts),
                                      ('/contas/(.*)/new/', CustomerNew),
                                      ('/contas/(.*)/(.*)/delete/', CustomerDelete),
                                      ('/contas/(.*)/(.*)/', CustomerDetails),
                                      ('/contas/(.*)/', AccountDetails),
                                      ('/categorias/', Categories),
                                      ('/categorias/([^/]+)/', Categories),
                                      ('/categorias/([^/]+)/', Categories),
                                      ('/despesas/', Expenses),
                                      ('/despesas/([^/]+)/', Expense),
                                      ('/despesas/([^/]+)/delete/', ExpenseDelete),
                                      ], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
