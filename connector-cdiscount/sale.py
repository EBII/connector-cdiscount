# -*- coding: utf-8 -*-
from .backend import cdiscount
from openerp.addons.connector.connector.queue.job import job
from openerp.addons.connector.connector.unit.backend_adapter import CRUDAdapter
from .connector import get_environment
from openerp.addons.connector.connector.unit.synchronizer import (Importer)
import logging
#from openerp import http, models, api, fields, _



_logger = logging.getLogger(__name__)


@job(default_channel='root.cdiscount')
def sale_order_import_batch(session, model_name, backend_id, filters=None):
    """ Prepare a batch import of records from Magento """
    env =  get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(SaleOrderBatchImport)
    importer.run()

@cdiscount
class CdiscountAdapter(CRUDAdapter):

    def search_read(self):
        return [{'order': 'num1'},{'order':'num2'}]

@job
def import_record_sale_order(self0):
    pass

@cdiscount
class SaleOrderBatchImport(Importer):
    _model_name = ['cdiscount.sale.order']

    def _import_record(self, record_id, **kwargs):
        """ Import the record directly """
        uuid = import_record_sale_order.delay(self.session,
                        self.model._name,
                        self.backend_record.id,
                        record_id,
                        **kwargs)
        # todo ajouter la pièce jointe
        # https://github.com/OCA/connector-interfaces/blob/9.0/base_import_async/models/base_import_async.py
#
    def run(self):
        """ Run the synchronization """
        records = self.backend_adapter.search_read()
        _logger.info('search ...')
        for record in records:
            self._import_record(record)