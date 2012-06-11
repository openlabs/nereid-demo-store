# -*- coding: utf-8 -*-
"""
    checkout

    Disable guest checkout for now

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelSQL
from trytond.pool import Pool
from nereid import login_required, render_template, request

from .i18n import _

class DefaultCheckout(ModelSQL):
    'Default checkout functionality'
    _name = 'nereid.checkout.default'


    @login_required
    def checkout(self):
        return super(DefaultCheckout, self).checkout()

    def _begin_registered(self):
        '''Begin checkout process for registered user.'''
        cart_obj = Pool().get('nereid.cart')
        from trytond.modules.nereid_checkout.forms import OneStepCheckoutRegd

        cart = cart_obj.open_cart()

        form = OneStepCheckoutRegd(request.form)
        addresses = [(0, _('New Address'))] + cart_obj._get_addresses()
        form.billing_address.choices = addresses
        form.shipping_address.choices = addresses
        form.payment_method.choices = [
            (m.id, m.name) for m in request.nereid_website.allowed_gateways
        ]

        return render_template('checkout.jinja', form=form, cart=cart)

    def _submit_registered(self):
        '''Submission when registered user'''
        cart_obj = Pool().get('nereid.cart')
        sale_obj = Pool().get('sale.sale')
        from trytond.modules.nereid_checkout.forms import OneStepCheckoutRegd

        form = OneStepCheckoutRegd(request.form)
        addresses = cart_obj._get_addresses()
        form.billing_address.choices.extend(addresses)
        form.shipping_address.choices.extend(addresses)
        form.payment_method.choices = [
            (m.id, m.name) for m in request.nereid_website.allowed_gateways
        ]
        form.shipment_method.validators = []

        cart = cart_obj.open_cart()
        if form.validate():
            # Get billing address
            if form.billing_address.data == 0:
                # New address
                billing_address = self._create_address(
                    form.new_billing_address.data)
            else:
                billing_address = form.billing_address.data

            # Get shipping address
            shipping_address = billing_address
            if not form.shipping_same_as_billing:
                if form.shipping_address.data == 0:
                    shipping_address = self._create_address(
                        form.new_shipping_address.data)
                else:
                    shipping_address = form.shipping_address.data

            # Write the information to the order
            sale_obj.write(cart.sale.id, {
                'invoice_address'    : billing_address,
                'shipment_address'   : shipping_address,
                })

        return form, form.validate()

DefaultCheckout()
