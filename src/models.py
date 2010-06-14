# -*- coding: utf-8 -*-
from aetycoon import DerivedProperty, TransformProperty
from django.template.defaultfilters import slugify
from google.appengine.ext import db


class Account(db.Model):
    user = db.UserProperty()
    name = db.StringProperty(required=True, verbose_name="nome")
    n_customers = db.IntegerProperty(default=0)

    @DerivedProperty
    def slug(self):
        return str(slugify(self.name))

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/contas/%s/" % self.slug


class Customer(db.Model):
    account = db.ReferenceProperty(Account, verbose_name="conta")

    name = db.StringProperty(verbose_name="nome", required=True)
    status = db.StringProperty(choices=["ativo", "desativado", "reativado"], default="ativo")
    email = db.EmailProperty(verbose_name="e-mail")

    address = db.StringProperty(multiline=True, verbose_name="endereço")
    city = db.StringProperty(default="Porto Alegre", verbose_name="cidade")
    state = db.StringProperty(default="RS", verbose_name="estado")
    country = db.StringProperty(default="BR", verbose_name="país")
    zip_code = db.PostalAddressProperty(verbose_name="CEP")

    birth = db.DateProperty(verbose_name="data nascimento")
    phone = db.PhoneNumberProperty(verbose_name="telefone")
    occupation = db.StringProperty(verbose_name="ocupação")

    responsible = db.StringProperty(verbose_name="médico responsável")

    remmarks = db.TextProperty(verbose_name="observações")

    date_first_contact = db.DateTimeProperty(verbose_name="data cadastro")

    date_added = db.DateTimeProperty(auto_now_add=True)
    date_modified = db.DateTimeProperty(auto_now=True)

    @DerivedProperty
    def slug(self):
        return str(slugify(self.name))

    def get_absolute_url(self):
        return "%s%s/" % (self.account.get_absolute_url(), self.slug)


class Category(db.Model):
    TYPE_CHOICES = (('Custo'),
                    ('Receita'))

    user = db.UserProperty()
    parent_category = db.SelfReferenceProperty(collection_name='child_categories',
                                               verbose_name='categoria mãe')
    type = db.StringProperty(required=True,
                             default='Custo',
                             choices=TYPE_CHOICES,
                             verbose_name='tipo')
    name = db.StringProperty(required=True, verbose_name='nome')
    date_added = db.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.name

def prefetch_refprop(entities, prop):
    ref_keys = [prop.get_value_for_datastore(x) for x in entities]
    existing_ref_keys = set(filter(lambda key: key is not None, ref_keys))
    ref_entities = dict((x.key(), x) for x in db.get(existing_ref_keys))
    for entity, ref_key in zip(entities, ref_keys):
        prop.__set__(entity, ref_entities[ref_key])
    return entities
