# -*- coding: utf-8 -*-
"""
    User

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL
from trytond.pool import Pool

class User(ModelSQL, ModelView):
    "User"
    _name = "res.user"

    def __init__(self):
        self._error_messages.update({
            'cannot_create': 'For security reasons creating users is disabled',
            'security_check': 'For security reasons this op is not allowed'
        })

    def create(self, vals):
        self.raise_user_error('cannot_create')

    def write(self, ids, vals):
        if set([
            'password', 'groups', 
            'rule_groups', 'salt', ]).intersection(vals.keys()):
            self.raise_user_error('cannot_change_password')
        return super(User, self).write(ids, vals)

User()      
