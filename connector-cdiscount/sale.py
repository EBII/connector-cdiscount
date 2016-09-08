# -*- coding: utf-8 -*-

import os
from .backend import cdiscount
from openerp.addons.connector.queue.job import job
from openerp import http, models, api, fields, _
#from tests.orderhash import HASH as listHash
from tests.getSales import do_the_job
import json
from .unit.tools import get_or_create_partner, create_quotations ,add_item_to_quotations
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
from unit.serialize_json import json_to_data
from .connector import get_environment
from openerp.addons.connector.unit.synchronizer import (Importer)
from openerp.addons.connector.session import ConnectorSession
from datetime import date
import logging
#from openerp import http, models, api, fields, _
from cStringIO import StringIO
#
# OPTIONS = {
#          'OPT_SEPARATOR': ',',
#          'OPT_QUOTING': '"',
#          'OPT_HAS_HEADER': False,
#         'OPT_ENCODING': 'utf-8',
#      }
# options defined in base_import/import.js
#OPT_HAS_HEADER = 'headers'
#OPT_SEPARATOR = 'separator'
#OPT_QUOTING = 'quoting'
#OPT_ENCODING = 'encoding'


_logger = logging.getLogger(__name__)


@job(default_channel='root.cdiscount')
def sale_order_import_batch(session, model_name, backend_id, filters=None):
    """ Prepare a batch import of sales to validate from Cdiscount """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(SaleOrderBatchImport)
    importer.run(filters=filters)


@cdiscount
class CdiscountAdapter(CRUDAdapter):
    _model_name = 'cdiscount.sale.order'

    def search_read(self, filters=None):

        listHash = do_the_job('toto', 'tutu', 0 )
        #_logger.info("search_read: %s", str(len(listHash)))
        return listHash
        #return [{'order': 'num1','OrderNumber':'ON1'},{'order':'num2','OrderNumber':'ON2'}]

@cdiscount
class CdiscountSaleOrderImporter(Importer):
    _model_name = ['sale.order',]

    def _must_skip(self):
        if self.binder.to_openerp(self.cdiscount_id):
            return _('Already imported')

    def _get_data(self, attachment_id):
        attachment = self.env['ir.attachment'].browse( attachment_id)
        _logger.info(attachment.datas)
        return json.loads(attachment.datas)

    def _import_dependency(self):
        # TODO importer les partenaires..*[]:
        pass

    def _create_data(self):
        """mapper le record en h odoo """
        data = self.cdiscount_record

    def _map_data(self):
        """ Returns an instance of
        :py:class:`~openerp.addons.connector.unit.mapper.MapRecord`

        """
        return self.mapper.map_record(self.cdiscount_record)

    def run(self, attachment_id, force=False):
        """ Run the synchronization
        """
        self.cdiscount_record = self._get_data(attachment_id)
        self.cdiscount_id = self.cdiscount_record['OrderId']
        skip = self._must_skip()
        if skip:
            return skip

        binding = self._get_binding()

        self._import_dependencies()

        map_record = self._map_data()

        record = self._create_data(map_record)
        binding = self._create(record)

        self.binder.bind(self.cdiscount_id, binding)


@job
def import_record_sale_order(session, model, att_id,backend_id ):
    "Sale Imported from Cdiscount to validate it in Quotations "
    env = get_environment(session, 'sale.order', backend_id)
    importer = env.get_connector_unit(CdiscountSaleOrderImporter)
    importer.run(att_id)


# class fake():
#     _logger.info("cette command: %s ", attachment['OrderNumber'])
#     # Extraire  3 contact depuis record => si nouveau creer res_partner principal (ajouter id cdiscount )
#     #
#     partner_customer_id, partner_billing_id, partner_shipping_id = get_or_create_partner(session,record)
#
#     _logger.info(str(partner_customer_id))
#     _logger.info(str(partner_billing_id))
#     _logger.info( str(partner_shipping_id))
#
#     # create sale_quotations
#     #
#     values =  {'partner_id':partner_customer_id,
#                'partner_invoice_id':partner_billing_id,
#                'partner_shipping_id':partner_shipping_id,
#                'client_order_ref' : attachment['Order']['OrderNumber'],
#                'warehouse_id' : 1, }
#     quotation_id = create_quotations(session,values)
#
#     _logger.info('creation du devis : ' + str(quotation_id))
#     order_lines = attachment['Order']['OrderLineList']
#
#     # Attachement de la piece jointes au nouveau devis
#     #
#     session.env['ir.attachment'].browse(att_id)\
#         .write({'res_model': 'sale.order',
#                 'res_id': quotation_id,
#                 })
#
#     _logger.info('attachement de la piece jointes au devis %s',  str(att_id))
#     _logger.info ('longeur' + str(len(order_lines)))
#     _logger.info('les lignes : ' + str(order_lines))
#     _logger.info(type(order_lines))
#
#     #Selon le nombre de ligne de produits dans la commande (ajuster avec le DICO  reel
#     if len(order_lines) > 1:
#
#         for order_line in order_lines:
#             _logger.info('Orderline:'  + str(order_line))
#             price_unit = order_line['PurchasePrice']
#             line_values = {'order_id': quotation_id, 'product_uom_qty': order_line['Quantity'],'price_unit': price_unit ,'name': order_line['SellerProductId'], }
#             add_item_to_quotations(session, line_values)
#     else:
#         price_unit = round(float(order_lines['OrderLine']['PurchasePrice']), 2)
#         line_values = {'order_id': quotation_id, 'product_uom_qty': order_lines['OrderLine']['Quantity'],'price_unit': price_unit ,'name':order_lines['OrderLine']['SellerProductId'], }
#         add_item_to_quotations(session, line_values)
#
#     #lister les articles verfier existance
#     #utiliser des data qui contiennetn un code produit juste.. ou de demo dont le produit existe


def _link_attachment_to_job(session,file_name, job_uuid, att_id):

    job = session.env['queue.job'].search([('uuid', '=', job_uuid)], limit=1)
    #_logger.info("on attacherai  " + str(job.id)+" id attch: "+ str(att_id) )
    session.env['ir.attachment'].browse(att_id).write({
        'res_model': 'queue.job',
        'res_id': job.id,
        'res_name':file_name,
        })



#genere un nom de fichier
def _getFilenameForSaleOrderJob(order_number):
    adate = date.today()
    return "Sale-"+str(adate)+"-"+str(order_number)


@cdiscount
class SaleOrderBatchImport(Importer):
    _model_name = ['cdiscount.sale.order']

    def _import_record(self, record, **kwargs):
        """ Import the record directly """
        #_logger.info("entree import_record %s ",  str(record))
        file_name = _getFilenameForSaleOrderJob(record['OrderNumber'])
        session = ConnectorSession.from_env(self.env)
         # create a CSV attachment and enqueue the job
        #root, ext = os.path.splitext(file_name)
        
        # ajouter la pièce jointe et utiliser les test
        # https://github.com/OCA/connector-interfaces/blob/9.0/base_import_async/models/base_import_async.py
        #https://github.com/OCA/connector-interfaces/blob/9.0/base_import_async/models/base_import_async.py#L172

        #_logger.info("le texte avant creation de la piece jointe : %s ", record_text)
        _logger.info("le file_name : %s ", file_name)

        att_id = _create_csv_attachment(session,
                                        record,
                                        file_name)

        # import pdb
        # pdb.set_trace()

        job_uuid = import_record_sale_order.delay(session,'ir.attachment',
                                                  att_id, self.backend_record.id)

        #_logger.info(u"job uuid generé : %s attachement id: %s ", str(job_uuid),str(att_id))
        _logger.info(u"et là on attache la piece joint au job")

        _link_attachment_to_job(session,file_name, job_uuid, att_id)


    def run(self, filters):
        """ Run the synchronization """
        records = self.backend_adapter.search_read(filters)
        _logger.info('search ...')
        #_logger.info('le h: '+ str(records))
        #PATH = ['Envelope']['Body']['GetOrderListResponse']['GetOrderListResult']['OrderList']['Order']
        if len(records['Envelope']['Body']['GetOrderListResponse']['GetOrderListResult']['OrderList']['Order']) >1 :
            _logger.info("multiple sales")
            for record in records['Envelope']['Body']['GetOrderListResponse']['GetOrderListResult']['OrderList']['Order']:
                #_logger.info(str(record))
                #print "je print chaque record : " + str(record)
               # _logger.info(record)
                self._import_record(record)
        else:
            #_logger.info("unique sales")
            record = records['Envelope']['Body']['GetOrderListResponse']['GetOrderListResult']['OrderList']['Order']
            #_logger.info(str(record))
                #print "je print chaque record : " + str(record)
            self._import_record(record)


def _create_csv_attachment(session, h_data, file_name):
    # write csv
    f = StringIO()
    json.dump(h_data,f)
    #writer = csv.writer(f ,  delimiter=str(OPTIONS['OPT_SEPARATOR']),  quotechar=str(OPTIONS['OPT_QUOTING']) )
    #encoding = (OPTIONS['OPT_ENCODING'])
   # writer.writerow(_encode(h_data.keys(), encoding))
    #values_json = data_to_json(h_data)
    _logger.info(json.dumps(h_data))
    #writer.writerow(json.dumps(h_data))
    # create attachment
    attachment = session.env['ir.attachment'].create({
        'name': file_name,
        'datas': f.getvalue().encode('base64')
    })
    return attachment.id

# def _encode(row, encoding):
#     #insert des delimiter à chaque caractères ??
#     #return[cell.encode(encoding) for cell in row]
#
#     return [row.encode(encoding)]
#
# def _decode(row, encoding):
#     return [cell.decode(encoding) for cell in row]
