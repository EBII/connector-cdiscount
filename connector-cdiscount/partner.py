# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .backend import cdiscount
import logging
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper
                                                  )
from openerp.addons.connector.exception import MappingError

class CdiscountResPartner(models.Model):
    _name = 'cdiscount.res.partner'
    _inherit = 'cdiscount.binding'
    _inherits = {'res.partner': 'openerp_id'}
    _description = 'Cdiscount Partner'

    _rec_name = 'name'

    openerp_id = fields.Many2one(comodel_name='res.partner',
                                 string='Partner',
                                 required=True,
                                 ondelete='cascade')
    backend_id = fields.Many2one(
        comodel_name='cdiscount.backend',
        string='Cdiscount Backend',
        store=True,
        readonly=True,
        # override 'cdiscount.binding', can't be INSERTed if True:
        required=False,
    )

    customer_id = fields.Char("cdicount_customer_id")

@cdiscount
class PartnerImportMapper(ImportMapper):
    _model_name = 'cdiscount.res.partner'
    direct = [
        ('title', 'Civility'),
        ('mobile', 'MobilePhone'),
        ('cdis_Id', 'CustomerId'),
        ('street', 'Street'),
        ('zip', 'ZipCode'),
        ('city', 'City'),

    ]

    # @only_create
    # @mapping
    # def is_company(self, record):
    #     # partners are companies so we can bind
    #     # addresses on them
    #     return {'is_company': True}

    @mapping
    def names(self, record):
        # TODO create a glue module for base_surname
        parts = [part for part in (record['FirstName'],
                                   record['LastName']) if part]
        return {'name': ' '.join(parts)}

    @mapping
    def customer_group_id(self, record):
        # import customer groups
        binder = self.binder_for(model='cdiscount.res.partner.category')
        category_id = binder.to_openerp(record['group_id'], unwrap=True)

        if category_id is None:
            raise MappingError("The partner category with "
                               "cdiscount id %s does not exist" %
                               record['group_id'])

        # FIXME: should remove the previous tag (all the other tags from
        # the same backend)
        return {'category_id': [(4, category_id)]}

    # @mapping
    # def website_id(self, record):
    #     binder = self.binder_for(model='cdiscount.website')
    #     website_id = binder.to_openerp(record['website_id'])
    #     return {'website_id': website_id}

    #@only_create
    @mapping
    def company_id(self, record):
        binder = self.binder_for(model='cdiscount.storeview')
        storeview = binder.to_openerp(record['store_id'], browse=True)
        if storeview:
            company = storeview.backend_id.company_id
            if company:
                return {'company_id': company.id}
        return {'company_id': False}

    @mapping
    def lang(self, record):
        binder = self.binder_for(model='cdiscount.storeview')
        storeview = binder.to_openerp(record['store_id'], browse=True)
        if storeview:
            if storeview.lang_id:
                return {'lang': storeview.lang_id.code}

    #@only_create
    @mapping
    def customer(self, record):
        return {'customer': True}

    @mapping
    def type(self, record):
        return {'type': 'default'}

   # @only_create
    @mapping
    def openerp_id(self, record):
        """ Will bind the customer on a existing partner
        with the same email """
        partner = self.env['res.partner'].search(
            [('email', '=', record['email']),
             ('customer', '=', True),
             '|',
             ('is_company', '=', True),
             ('parent_id', '=', False)],
            limit=1,
        )
        if partner:
            return {'openerp_id': partner.id}


