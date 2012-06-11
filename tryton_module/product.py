# -*- coding: utf-8 -*-
"""
    product


    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL
from trytond.pool import Pool

from nereid.contrib.pagination import Pagination
from nereid import request, render_template
from werkzeug.exceptions import NotFound


class Category(ModelSQL, ModelView):
    """
    Category
    """
    _name = "product.category"

    def __init__(self):
        super(Category, self).__init__()

        # Change the number of product per page to 12 from default value
        self.per_page = 12

    def render(self, uri, page=1):
        """
        Renders the template
        """
        product_obj = Pool().get('product.product')
        category_ids = self.search([
            ('displayed_on_eshop', '=', True),
            ('uri', '=', uri),
            ('sites', '=', request.nereid_website.id)
        ])
        if not category_ids:
            return NotFound('Product Category Not Found')

        # if only one product is found then it is rendered and 
        # if more than one are found then the first one is rendered
        category = self.browse(category_ids[0])
        child_categories = self.search([('childs', 'child_of', [category.id])])
        print child_categories
        products = Pagination(product_obj, [
            ('displayed_on_eshop', '=', True),
            ('category', 'in', child_categories + [category.id]),
        ], page=page, per_page=self.per_page)
        return render_template('category.jinja', category=category, 
            products=products,)

Category()
