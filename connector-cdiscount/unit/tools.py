# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)


def get_or_create_partner (session, record):
    if not record:
        return
    client_id= record['Order']['Customer']['CustomerId']
    code_country = record['Order']['ShippingAddress']['Country']
    country = session.env['res.country'].search([('code','ilike',code_country)])
    country_Id = country.id
    pids = session.env['res.partner'].search([('cdis_Id', 'ilike', client_id),('type','ilike','default')])
    _logger.info('create contact civility or get id:' + record['Order']['Customer']['Civility']+ 'pids:' + str(pids))

    if len(pids) != 1 :
        # le client nexiste pas
        customer_shortCivility = record['Order']['Customer']['Civility']
        customer_civility_id = getcivility_Id(session, customer_shortCivility)
        customer_partner_name = record['Order']['Customer']['FirstName'].title() + " " + record['Order']['Customer']['LastName'].title()
        #creation du respartner customer
        customer_values = {
              'title' : customer_civility_id,
              'type' : 'default',
              'cdis_Id': record['Order']['Customer']['CustomerId'],
              'name' : customer_partner_name,
              'mobile' :record['Order']['Customer']['MobilePhone'],
              'street': record['Order']['BillingAddress']['Street'],
              'zip': record['Order']['BillingAddress']['ZipCode'],
              'city': record['Order']['BillingAddress']['City'],
              'country_id': country_Id,
              'customer': True,
            }
        partner_customer = session.env['res.partner'].create(customer_values)
        #creation du respartner billing
        billing_shortCivility = record['Order']['Customer']['Civility']
        billing_civility_id = getcivility_Id(session, billing_shortCivility)
        billing_partner_name = record['Order']['BillingAddress']['FirstName'].title() + " " + record['Order']['BillingAddress']['LastName'].title()
        billing_values = {
                      'title' : billing_civility_id,
                      'type' : 'invoice',
                      'cdis_Id': record['Order']['OrderNumber'],
                      'name' : billing_partner_name,
                      #'mobile' :record['Order']['Customer']['MobilePhone'],
                      'street': record['Order']['BillingAddress']['Street'],
                      'zip': record['Order']['BillingAddress']['ZipCode'],
                      'city': record['Order']['BillingAddress']['City'],
                      'country_id': country_Id,
                      'customer': True,
                      'parent_id': partner_customer.id,
                    }
        partner_billing = session.env['res.partner'].create(billing_values)
        #creation du respartner shipping
        shippping_shortCivility = record['Order']['Customer']['Civility']
        shippping_civility_id = getcivility_Id(session, shippping_shortCivility)
        shippping_partner_name = record['Order']['ShippingAddress']['FirstName'].title() + " " + record['Order']['ShippingAddress']['LastName'].title()
        shipping_values = {
                      'title' : shippping_civility_id,
                      'type' : 'delivery',
                      'cdis_Id': record['Order']['OrderNumber'],
                      'name' : shippping_partner_name,
                      #'mobile' :record['Order']['Customer']['MobilePhone'],
                      'street': record['Order']['ShippingAddress']['Street'],
                      'zip': record['Order']['ShippingAddress']['ZipCode'],
                      'city': record['Order']['ShippingAddress']['City'],
                      'country_id': country_Id,
                      'customer': True,
                      'parent_id': partner_customer.id,
                    }
        partner_shipping = session.env['res.partner'].create(shipping_values)

    else:
        #le client existe déjà
        _logger.info('le client exist deja')
        partner_customer = pids
        billing_shortCivility = record['Order']['Customer']['Civility']
        billing_civility_id = getcivility_Id(session, billing_shortCivility)
        billing_partner_name = record['Order']['BillingAddress']['FirstName'].title() + " " + record['Order']['BillingAddress']['LastName'].title()
        billing_values = {
                      'title' : billing_civility_id,
                      'type' : 'invoice',
                      'cdis_Id': record['Order']['OrderNumber'],
                      'name' : billing_partner_name,
                      #'mobile' :record['Order']['Customer']['MobilePhone'],
                      'street': record['Order']['BillingAddress']['Street'],
                      'zip': record['Order']['BillingAddress']['ZipCode'],
                      'city': record['Order']['BillingAddress']['City'],
                      'country_id': country_Id,
                      'customer': True,
                      'parent_id':pids.id
                    }
        partner_billing = session.env['res.partner'].create(billing_values)

       #creation du respartner shipping
        shippping_shortCivility = record['Order']['Customer']['Civility']
        shippping_civility_id = getcivility_Id(session, shippping_shortCivility)
        shippping_partner_name = record['Order']['ShippingAddress']['FirstName'].title() + " " + record['Order']['ShippingAddress']['LastName'].title()
        shipping_values = {
                      'title' : shippping_civility_id,
                      'type' : 'delivery',
                      'cdis_Id': record['Order']['OrderNumber'],
                      'name' : shippping_partner_name,
                      #'mobile' :record['Order']['Customer']['MobilePhone'],
                      'street': record['Order']['ShippingAddress']['Street'],
                      'zip': record['Order']['ShippingAddress']['ZipCode'],
                      'city': record['Order']['ShippingAddress']['City'],
                      'country_id': country_Id,
                      'customer': True,
                      'parent_id':pids.id,
                    }
        partner_shipping = session.env['res.partner'].create(shipping_values)

    return partner_customer.id, partner_billing.id ,partner_shipping.id


def getcivility_Id(session, shortcut):
    if not shortcut:
        return
    title = session.env['res.partner.title'].search(
           [('domain', '=', 'contact'),
            ('shortcut', '=ilike', shortcut)],
           limit=1)
    if not title:
       title = session.env['res.partner.title'].create(
           {'domain': 'contact',
            'shortcut': shortcut.title(),
            'name': shortcut,
            })
    _logger.info('id civility: ' +str(title))
    return title.id

def create_quotations(session,values):

    quotation_id = session.env['sale.order'].create(values)
    return quotation_id.id

def add_item_to_quotations(session, values):

    items_id = session.env['sale.order.line'].create(values)
    return True

