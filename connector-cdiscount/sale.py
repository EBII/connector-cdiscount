# -*- coding: utf-8 -*-

import os
from .backend import cdiscount
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
from .connector import get_environment
from openerp.addons.connector.unit.synchronizer import (Importer)
from openerp.addons.connector.session import ConnectorSession
from datetime import date
import logging
#from openerp import http, models, api, fields, _
from cStringIO import StringIO
import csv
OPTIONS = {
         'OPT_SEPARATOR': ',',
         'OPT_QUOTING': '"',
         'OPT_HAS_HEADER': True,
        'OPT_ENCODING': 'utf-8',
     }
# options defined in base_import/import.js
#OPT_HAS_HEADER = 'headers'
#OPT_SEPARATOR = 'separator'
#OPT_QUOTING = 'quoting'
#OPT_ENCODING = 'encoding'


_logger = logging.getLogger(__name__)


@job(default_channel='root.cdiscount')
def sale_order_import_batch(session, model_name, backend_id, filters=None):
    """ Prepare a batch import of records from Magento """
    env =  get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(SaleOrderBatchImport)
    importer.run(filters=filters)

@cdiscount
class CdiscountAdapter(CRUDAdapter):
    _model_name = ['cdiscount.sale.order']

    def search_read(self, filters=None):
        return [{'order': 'num1','OrderNumber':'ON1'},{'order':'num2','OrderNumber':'ON2'}]

@job
def import_record_sale_order(session, att_id,record):
    print "00"
    pass

def _link_attachment_to_job(session, job_uuid, att_id):
    job = session.env['queue.job'].search([('uuid', '=', job_uuid)], limit=1)
    session.env['ir.attachment'].browse(att_id).write({
        'res_model': 'queue.job',
        'res_id': job.id,
})

def _getFilenameForSaleOrderJob(order_number):
    adate = date.today()
    return "Sale-"+str(adate)+"-"+str(order_number)


@cdiscount
class SaleOrderBatchImport(Importer):
    _model_name = ['cdiscount.sale.order']

    def _import_record(self, record, **kwargs):
        """ Import the record directly """
        print record
        file_name = _getFilenameForSaleOrderJob(record['OrderNumber'])
        session = ConnectorSession.from_env(self.env)
         # create a CSV attachment and enqueue the job
        root, ext = os.path.splitext(file_name)
        att_id = _create_csv_attachment(session,
                                        record,
                                        file_name)

        job_uuid = import_record_sale_order.delay(session,
                                          att_id,
                                          record)
        _link_attachment_to_job(session, job_uuid, att_id)

        # todo ajouter la pièce jointe et utiliser les test
        # https://github.com/OCA/connector-interfaces/blob/9.0/base_import_async/models/base_import_async.py
        #https://github.com/OCA/connector-interfaces/blob/9.0/base_import_async/models/base_import_async.py#L172

    def run(self, filters):
        """ Run the synchronization """
        records = self.backend_adapter.search_read(filters)
        _logger.info('search ...')
        for record in records:
            self._import_record(record)



def _create_csv_attachment(session, h_data, file_name):
    # write csv
    f = StringIO()
    writer = csv.writer(f,
                        delimiter=str(OPTIONS['OPT_SEPARATOR']),
                        quotechar=str(OPTIONS['OPT_QUOTING']))
    encoding = (OPTIONS['OPT_ENCODING'])
    writer.writerow(_encode(h_data.keys(), encoding))
    writer.writerow(_encode(h_data.values(), encoding))
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
