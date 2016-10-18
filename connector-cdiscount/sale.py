# -*- coding: utf-8 -*-

import os
from .backend import cdiscount
from openerp.addons.connector.queue.job import job
import openerp.addons.decimal_precision as dp
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
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper
                                                  )
from openerp.addons.connector_ecommerce.sale import ShippingLineBuilder
from openerp.addons.connector.exception import MappingError
from .unit.mapper import normalize_datetime
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


class CdiscountSaleOrder(models.Model):
    _name = 'cdiscount.sale.order'
    _inherit = 'cdiscount.binding'
    _description = 'Cdiscount Sale Order'
    _inherits = {'sale.order': 'openerp_id'}

    openerp_id = fields.Many2one(comodel_name='sale.order',
                                 string='Sale Order',
                                 required=True,
                                 ondelete='cascade')
    cdiscount_order_line_ids = fields.One2many(
        comodel_name='cdiscount.sale.order.line',
        inverse_name='cdiscount_order_id',
        string='Cdiscount Order Lines'
    )
    total_amount = fields.Float(
        string='Total amount',
        digits_compute=dp.get_precision('Account')
    )
    total_amount_tax = fields.Float(
        string='Total amount w. tax',
        digits_compute=dp.get_precision('Account')
    )
    cdiscount_order_id = fields.Integer(string='Cdiscount Order ID',
                                      help="'order_id' field in Cdiscount")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cdiscount_bind_ids = fields.One2many(
        comodel_name='cdiscount.sale.order',
        inverse_name='openerp_id',
        string="Cdiscount Bindings",
    )

class CdiscountSaleOrderLine(models.Model):
    _name = 'cdiscount.sale.order.line'
    _inherit = 'cdiscount.binding'
    _description = 'Cdiscount Sale Order Line'
    _inherits = {'sale.order.line': 'openerp_id'}

    cdiscount_order_id = fields.Many2one(comodel_name='cdiscount.sale.order',
                                       string='Cdiscount Sale Order',
                                       required=True,
                                       ondelete='cascade',
                                       select=True)
    openerp_id = fields.Many2one(comodel_name='sale.order.line',
                                 string='Sale Order Line',
                                 required=True,
                                 ondelete='cascade')
    backend_id = fields.Many2one(
        related='cdiscount_order_id.backend_id',
        string='Cdiscount Backend',
        readonly=True,
        store=True,
        # override 'cdiscount.binding', can't be INSERTed if True:
        required=False,
    )
    tax_rate = fields.Float(string='Tax Rate',
                            digits_compute=dp.get_precision('Account'))
    notes = fields.Char()

    @api.model
    def create(self, vals):
        cdiscount_order_id = vals['cdiscount_order_id']
        binding = self.env['cdiscount.sale.order'].browse(cdiscount_order_id)
        vals['order_id'] = binding.openerp_id.id
        binding = super(CdiscountSaleOrderLine, self).create(vals)
        # FIXME triggers function field
        # The amounts (amount_total, ...) computed fields on 'sale.order' are
        # not triggered when cdiscount.sale.order.line are created.
        # It might be a v8 regression, because they were triggered in
        # v7. Before getting a better correction, force the computation
        # by writing again on the line.
        line = binding.openerp_id
        line.write({'price_unit': line.price_unit})
        return binding


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    cdiscount_bind_ids = fields.One2many(
        comodel_name='cdiscount.sale.order.line',
        inverse_name='openerp_id',
        string="Cdiscount Bindings",
    )

@cdiscount
class SaleOrderImportMapper(ImportMapper):
    _model_name = 'cdiscount.sale.order'

    direct = [
              ('Status', 'state'),
              ('CreationDate', 'date_order'),
              ]

    #children = [('items', 'OrderLineList', 'cdiscount.sale.order.line'),]

    def _add_shipping_line(self, map_record, values):
        record = map_record.source
        amount_incl = float(record.get('InitialTotalAmount') or 0.0)
        amount_excl = float(record.get('InitialTotalShippingChargesAmount') or 0.0)
        if not (amount_incl or amount_excl):
            return values
        line_builder = self.unit_for(CdiscountShippingLineBuilder)
        if self.options.tax_include:
            discount = float(record.get('shipping_discount_amount') or 0.0)
            line_builder.price_unit = (amount_incl - discount)
        else:
            line_builder.price_unit = amount_excl

        if values.get('carrier_id'):
            carrier = self.env['delivery.carrier'].browse(values['carrier_id'])
            line_builder.product = carrier.product_id

        line = (0, 0, line_builder.get_line())
        values['order_line'].append(line)
        return values

    # def _add_cash_on_delivery_line(self, map_record, values):
    #     record = map_record.source
    #     amount_excl = float(record.get('cod_fee') or 0.0)
    #     amount_incl = float(record.get('cod_tax_amount') or 0.0)
    #     if not (amount_excl or amount_incl):
    #         return values
    #     line_builder = self.unit_for(CdiscountCashOnDeliveryLineBuilder)
    #     tax_include = self.options.tax_include
    #     line_builder.price_unit = amount_incl if tax_include else amount_excl
    #     line = (0, 0, line_builder.get_line())
    #     values['order_line'].append(line)
    #     return values
    #
    # def _add_gift_certificate_line(self, map_record, values):
    #     record = map_record.source
    #     if 'gift_cert_amount' not in record:
    #         return values
    #     # if gift_cert_amount is zero
    #     if not record.get('gift_cert_amount'):
    #         return values
    #     amount = float(record['gift_cert_amount'])
    #     line_builder = self.unit_for(CdiscountGiftOrderLineBuilder)
    #     line_builder.price_unit = amount
    #     if 'gift_cert_code' in record:
    #         line_builder.gift_code = record['gift_cert_code']
    #     line = (0, 0, line_builder.get_line())
    #     values['order_line'].append(line)
    #     return values
    #
    # def finalize(self, map_record, values):
    #     values.setdefault('order_line', [])
    #     values = self._add_shipping_line(map_record, values)
    #     values = self._add_cash_on_delivery_line(map_record, values)
    #     values = self._add_gift_certificate_line(map_record, values)
    #     values.update({
    #         'partner_id': self.options.partner_id,
    #         'partner_invoice_id': self.options.partner_invoice_id,
    #         'partner_shipping_id': self.options.partner_shipping_id,
    #     })
    #     onchange = self.unit_for(SaleOrderOnChange)
    #     return onchange.play(values, values['cdiscount_order_line_ids'])
    #
    @mapping
    def name(self, record):
        name = record['OrderNumber']
        prefix = "cdiscount-" #self.backend_record.sale_prefix
        if prefix:
            name = prefix + name
        return {'name': name}

    @mapping
    def customer_id(self, record):
        binder = self.binder_for('cdiscount.res.partner')

        partner_id = binder.to_openerp(record['Customer']['CustomerId'], unwrap=True)
        assert partner_id is not None, (
            "customer_id %s should have been imported in "
            "SaleOrderImporter._import_dependencies" % record['Customer']['CustomerId'])
        return {'partner_id': partner_id}

    # @mapping
    # def payment(self, record):
    #     record_method = record['payment']['method']
    #     method = self.env['payment.method'].search(
    #         [['name', '=', record_method]],
    #         limit=1,
    #     )
    #     assert method, ("method %s should exist because the import fails "
    #                     "in SaleOrderImporter._before_import when it is "http://localhost:8169/web?&debug=#menu_id=120&action=114
    #                     " missing" % record['payment']['method'])
    #     return {'payment_method_id': method.id}
    #
    # @mapping
    # def shipping_method(self, record):
    #     ifield = record.get('shipping_method')
    #     if not ifield:
    #         return
    #
    #     carrier = self.env['delivery.carrier'].search(
    #         [g('cdiscount_code', '=', ifield)],
    #         limit=1,
    #     )
    #     if carrier:
    #         result = {'carrier_id': carrier.id}
    #     else:
    #         fake_partner = self.env['res.partner'].search([], limit=1)
    #         product = self.env.ref(
    #             'connector_ecommerce.product_product_shipping')
    #         carrier = self.env['delivery.carrier'].create({
    #             'partner_id': fake_partner.id,
    #             'product_id': product.id,
    #             'name': ifield,
    #             'cdiscount_code': ifield})
    #         result = {'carrier_id': carrier.id}
    #     return result
    #
    # @mapping
    # def sales_team(self, record):
    #     team = self.options.storeview.section_id
    #     if team:
    #         return {'section_id': team.id}
    #
    # @mapping
    # def project_id(self, record):
    #     project_id = self.options.storeview.account_analytic_id
    #     if project_id:
    #         return {'project_id': project_id.id}
    #
    # @mapping
    # def fiscal_position(self, record):
    #     fiscal_position = self.options.storeview.fiscal_position_id
    #     if fiscal_position:
    #         return {'fiscal_position': fiscal_position.id}
    #
    # # partner_id, partner_invoice_id, partner_shipping_id
    # # are done in the importer
    #
    # @mapping
    # def backend_id(self, record):
    #     return {'backend_id': self.backend_record.id}
    #
    # @mapping
    # def user_id(self, record):
    #     """ Do not assign to a Salesperson otherwise sales orders are hidden
    #     for the salespersons (access rules)"""
    #     return {'user_id': False}
    #
    # @mapping
    # def sale_order_comment(self, record):
    #     comment_mapper = self.unit_for(SaleOrderCommentImportMapper)
    #     map_record = comment_mapper.map_record(record)
    #     return map_record.values(**self.options)
    #
    # @mapping
    # def pricelist_id(self, record):
    #     pricelist_mapper = self.unit_for(PricelistSaleOrderImportMapper)
    #     return pricelist_mapper.map_record(record).values(**self.options)
    #
    #


@cdiscount
class CdiscountShippingLineBuilder(ShippingLineBuilder):
    _model_name = 'cdiscount.sale.order'

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
    _model_name = ['cdiscount.sale.order',]

    def _must_skip(self):
        if self.binder.to_openerp(self.cdiscount_id):
            return _('Already imported')

    def _get_data(self, attachment_id):
        attachment = self.env['ir.attachment'].browse( attachment_id)
        _logger.info((attachment.datas).decode('base64'))
        data_decoded = (attachment.datas).decode('base64')
        return json.loads(data_decoded)

    def _import_dependency(self):
        # TODO importer les partenaires..*[]:
        pass

    def _create_data(self, map_record, **kwargs):
        return map_record.values(for_create=True, **kwargs)

    def _map_data(self):
        """ Returns an instance of
        :py:class:`~openerp.addons.connector.unit.mapper.MapRecord`

        """
        return self.mapper.map_record(self.cdiscount_record)

    def _import_dependencies(self):
        """
        importer les besoins de dependances produit sale partner etc..
        """
        self._import_addresses()

    def _import_addresses(self):

        partner_mapper = self.unit_for(ImportMapper, model='cdiscount.res.partner') #(TODO creer la classe en questionn)

        def create_partner(partner_record, parent_partner=None):

            map_record = partner_mapper.map_record(partner_record)
            data = map_record.values(for_create=True,
                                  parent_partner=parent_partner)
            return self.env['res.partner'].create(data)

        record = self.record
        client_id = record['Customer']['CustomerId']
        pids = self.env['res.partner'].search([('cdis_Id', 'ilike', client_id), ('type', 'ilike', 'default')])

        if len(pids) != 1 : # voir avec la classe bind #TODO
            # updatde
            _logger.info("need update partner")
            pass
        else:
            self.partner = create_partner(record['Customer'])

        self.billing = create_partner(record['BillingAddress'], self.partner)
        self.shipping = create_partner(record['ShippingAddress'], self.partner)

        return

    def _get_binding(self):
        _logger.info("get binding 391")
        return self.binder.to_openerp(self.cdiscount_id, browse=True)

    def _create(self, record):

        _logger.info("Methode create %s" ,str(record))

    def run(self, attachment_id, force=False):
        """ Run the synchronization
        """
        self.cdiscount_record = self._get_data(attachment_id)

        _logger.info("keys cdiscount record: %s",self.cdiscount_record.keys())

        self.cdiscount_id = self.cdiscount_record['OrderNumber']
        _logger.info("Order Number: %s" % self.cdiscount_id)

      #  self._import_dependencies(self.cdiscount_id,'cdiscount.sale.order')
        #
        # import pdb
        # pdb.set_trace()

        skip = self._must_skip()
        if skip:
            return skip

        map_record = self._map_data()


        record = self._create_data(map_record)
        #import pdb
        #pdb.set_trace()

        binding = self._create(record)

        #self.binder.bind(self.cdiscount_id, binding)


@job
def import_record_sale_order(session, model, att_id,backend_id ):
    "Sale Imported from Cdiscount to validate it in Quotations "
    env = get_environment(session, 'cdiscount.sale.order', backend_id)
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

