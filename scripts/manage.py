# -*- coding: utf-8 -*-
"""
    manage

    A script to manage the catalog

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from mongoengine import connect, Document


class Category(Document):
    """
    Category
    """
    name = StringField()

class Product(Document):
    """
    Product Sepcification
    """

