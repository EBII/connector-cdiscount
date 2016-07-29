# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.addons.connector.session import ConnectorSession
from .sale import SaleOrderBatchImport


class CcdiscountBackend(models.Model):
    _name = 'cdiscount.backend'
    _description = 'cdiscount Backend'
    _inherit = 'connector.backend'

    _backend_type = 'cdiscount'

    @api.model
    def _select_versions(self):
        """ Available versions

        Can be inherited to add custom versions.
                         """
        return [('01/08/2016', 'Version Actuelle'),]

    version = fields.Selection(
         selection='_select_versions',
         string='Version',
         required=True,
    )
    location = fields.Char(string='Location')
    username = fields.Char(string='Username')
    password = fields.Char(string='Password')
    default_lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Default Language',
    )

    @api.multi
    def import_sale_orders(self):
        session = ConnectorSession(self.env.cr, self.env.uid,
            context=self.env.context)
        for backend in self:
            SaleOrderBatchImport.delay(
              #  session,
                'cdiscount.sale.order',
                backend.id,
                priority=1)  # executed as soon as possible
        return True

    @api.model
    def _cdiscount_backend(self, callback, domain=None):
        if domain is None:
            domain = []
        backends = self.search(domain)
        if backends:
            getattr(backends, callback)()

    @api.model
    def _scheduler_import_sale_orders(self, domain=None):
        self._cdiscount_backend('import_sale_orders', domain=domain)
