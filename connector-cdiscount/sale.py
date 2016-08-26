# -*- coding: utf-8 -*-

import os
from .backend import cdiscount
from openerp.addons.connector.queue.job import job
#from tests.orderhash import HASH as listHash
from tests.getSales import do_the_job
import json
from .unit.tools import get_or_create_partner, create_quotations ,add_item_to_quotations
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
         'OPT_SEPARATOR': ';',
         'OPT_QUOTING': '"',
         'OPT_HAS_HEADER': False,
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
    """ Prepare a batch import of sales to validate from Cdiscount """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(SaleOrderBatchImport)
    importer.run(filters=filters)


@cdiscount
class CdiscountAdapter(CRUDAdapter):
    _model_name = ['cdiscount.sale.order']

    def search_read(self, filters=None):

        listHash = do_the_job('toto', 'tutu', 0 )
        _logger.info("search_read: "+str(len(listHash)))
        return listHash
        #return [{'order': 'num1','OrderNumber':'ON1'},{'order':'num2','OrderNumber':'ON2'}]


@job
def import_record_sale_order(session, att_id,record):
    "Sale Imported from Cdiscount to validate it in Quotations "

    _logger.info( "cette command: "+record['Order']['OrderNumber']+" ")
    # Extraire un 3 contact depuis record => si nouveau creer res_partner principal (ajouter id cdiscount )
    #
    partner_customer_id, partner_billing_id, partner_shipping_id = get_or_create_partner(session,record)

    _logger.info(str(partner_customer_id))
    _logger.info(str(partner_billing_id))
    _logger.info( str(partner_shipping_id))

    # create sale_quotations
    #
    values =  {'partner_id':partner_customer_id,
               'partner_invoice_id':partner_billing_id,
               'partner_shipping_id':partner_shipping_id,
               'client_order_ref' : record['Order']['OrderNumber'],
               'warehouse_id' : 1, }
    quotation_id = create_quotations(session,values)

    _logger.info('creation du devis : ' + str(quotation_id))
    order_lines = record['Order']['OrderLineList']

    # Attachement de la piece jointes au nouveau devis
    #
    session.env['ir.attachment'].browse(att_id)\
        .write({'res_model': 'sale.order',
                'res_id': quotation_id,
                })

    _logger.info('attachement de la piece jointes au devis' + str(att_id))
    _logger.info ('longeur' + str(len(order_lines)))
    _logger.info('les lignes : ' + str(order_lines))
    _logger.info(type(order_lines))

    #Selon le nombre de ligne de produits dans la commande (ajuster avec le DICO  reel
    if len(order_lines) > 1:

        for order_line in order_lines:
            _logger.info('Orderline:'  + str(order_line))
            price_unit = order_line['PurchasePrice']
            line_values = {'order_id': quotation_id, 'product_uom_qty': order_line['Quantity'],'price_unit': price_unit ,'name': order_line['SellerProductId'], }
            add_item_to_quotations(session, line_values)
    else:
        price_unit = round(float(order_lines['OrderLine']['PurchasePrice']), 2)
        line_values = {'order_id': quotation_id, 'product_uom_qty': order_lines['OrderLine']['Quantity'],'price_unit': price_unit ,'name':order_lines['OrderLine']['SellerProductId'], }
        add_item_to_quotations(session, line_values)

    #lister les articles verfier existance
    #utiliser des data qui contiennetn un code produit juste.. ou de demo dont le produit existe


def _link_attachment_to_job(session,file_name, job_uuid, att_id):

    job = session.env['queue.job'].search([('uuid', '=', job_uuid)], limit=1)
    _logger.info("on attacherai  " + str(job.id)+" id attch: "+ str(att_id) )
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
        _logger.info("entree import_record "+ str(record))
        file_name = _getFilenameForSaleOrderJob(record['Order']['OrderNumber'])
        session = ConnectorSession.from_env(self.env)
         # create a CSV attachment and enqueue the job
        #root, ext = os.path.splitext(file_name)
        record_text= str(record)
        # ajouter la pièce jointe et utiliser les test
        # https://github.com/OCA/connector-interfaces/blob/9.0/base_import_async/models/base_import_async.py
        #https://github.com/OCA/connector-interfaces/blob/9.0/base_import_async/models/base_import_async.py#L172

        _logger.info("le texte avant creation de la piece jointe : "+ record_text)
        _logger.info("le file_name : "+ file_name)

        att_id = _create_csv_attachment(session,
                                        record,
                                        file_name)

        job_uuid = import_record_sale_order.delay(session,
                                          att_id,
                                          record)
        _logger.info(u"job uuid generé : "+str(job_uuid)+ " attachement id: "+str(att_id))
        _logger.info(u"et là on attache la piece joint au job")

        _link_attachment_to_job(session,file_name, job_uuid, att_id)


    def run(self, filters):
        """ Run the synchronization """
        records = self.backend_adapter.search_read(filters)
        _logger.info('search ...')
        for record in records:
                #print "je print chaque record : " + str(record)
                _logger.info(record)
                self._import_record(record)



def _create_csv_attachment(session, h_data, file_name):
    # write csv
    f = StringIO()
    writer = csv.writer(f,
                        delimiter=str(OPTIONS['OPT_SEPARATOR']),
                        quotechar=str(OPTIONS['OPT_QUOTING'])
                        )
    encoding = (OPTIONS['OPT_ENCODING'])
   # writer.writerow(_encode(h_data.keys(), encoding))
    writer.writerow(_encode(str(h_data), encoding))
    # create attachment
    attachment = session.env['ir.attachment'].create({
        'name': file_name,
        'datas': f.getvalue().encode('base64')
    })
    return attachment.id

def _encode(row, encoding):
    #insert des delimiter à chaque caractères ??
    #return[cell.encode(encoding) for cell in row]
    return [row.encode(encoding)]

def _decode(row, encoding):
    return [cell.decode(encoding) for cell in row]
