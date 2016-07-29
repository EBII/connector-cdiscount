# -*- coding: utf-8 -*-
from .backend import cdiscount
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
from .connector import get_environment
from openerp.addons.connector.unit.synchronizer import (Importer)
import logging
#from openerp import http, models, api, fields, _
from cStringIO import StringIO
import csv
# OPTIONS = {
#         OPT_SEPARATOR: ',',
#         OPT_QUOTING: '"',
#         OPT_HAS_HEADER: True,
#     }
# options defined in base_import/import.js
OPT_HAS_HEADER = 'headers'
OPT_SEPARATOR = 'separator'
OPT_QUOTING = 'quoting'
OPT_ENCODING = 'encoding'


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
    print "00"
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
        # todo ajouter la pièce jointe et utiliser les test
        # https://github.com/OCA/connector-interfaces/blob/9.0/base_import_async/models/base_import_async.py
        uuid.attachment_id = _create_csv_attachment(self,record_id,**kwargs)



    def run(self):
        """ Run the synchronization """
        records = self.backend_adapter.search_read()
        _logger.info('search ...')
        for record in records:
            self._import_record(record)



def _create_csv_attachment(session, fields, data, options, file_name):
    # write csv
    f = StringIO()
    writer = csv.writer(f,
                        delimiter=str(options.get(OPT_SEPARATOR)),
                        quotechar=str(options.get(OPT_QUOTING)))
    encoding = options.get(OPT_ENCODING, 'utf-8')
    writer.writerow(_encode(fields, encoding))
    for row in data:
        writer.writerow(_encode(row, encoding))
    # create attachment
    attachment = session.env['ir.attachment'].create({
        'name': file_name,
        'datas': f.getvalue().encode('base64')
    })
    return attachment.id

def _encode(row, encoding):
    return [cell.encode(encoding) for cell in row]


def _decode(row, encoding):
    return [cell.decode(encoding) for cell in row]
