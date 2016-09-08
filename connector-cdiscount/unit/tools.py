# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)


def get_or_create_partner (session, record):
    if not record:
        return
    client_id= record['Customer']['CustomerId']
    code_country = record['ShippingAddress']['Country']
    country = session.env['res.country'].search([('code','ilike',code_country)])
    country_Id = country.id
    pids = session.env['res.partner'].search([('cdis_Id', 'ilike', client_id),('type','ilike','default')])
    _logger.info('create contact civility or get id:' + record['Customer']['Civility']+ 'pids:' + str(pids))

    if len(pids) != 1 :
        # le client nexiste pas
        customer_shortCivility = record['Customer']['Civility']
        customer_civility_id = getcivility_Id(session, customer_shortCivility)
        customer_partner_name = record['Customer']['FirstName'].title() + " " + record['Customer']['LastName'].title()
        #creation du respartner customer
        customer_values = {
              'title' : customer_civility_id,
              'type' : 'default',
              'cdis_Id': record['Customer']['CustomerId'],
              'name' : customer_partner_name,
              'mobile' :record['Customer']['MobilePhone'],
              'street': record['BillingAddress']['Street'],
              'zip': record['BillingAddress']['ZipCode'],
              'city': record['BillingAddress']['City'],
              'country_id': country_Id,
              'customer': True,
            }
        partner_customer = session.env['res.partner'].create(customer_values)
        #creation du respartner billing
        billing_shortCivility = record['Customer']['Civility']
        billing_civility_id = getcivility_Id(session, billing_shortCivility)
        billing_partner_name = record['BillingAddress']['FirstName'].title() + " " + record['BillingAddress']['LastName'].title()
        billing_values = {
                      'title' : billing_civility_id,
                      'type' : 'invoice',
                      'cdis_Id': record['OrderNumber'],
                      'name' : billing_partner_name,
                      #'mobile' :record['Customer']['MobilePhone'],
                      'street': record['BillingAddress']['Street'],
                      'zip': record['BillingAddress']['ZipCode'],
                      'city': record['BillingAddress']['City'],
                      'country_id': country_Id,
                      'customer': True,
                      'parent_id': partner_customer.id,
                    }
        partner_billing = session.env['res.partner'].create(billing_values)
        #creation du respartner shipping
        shippping_shortCivility = record['Customer']['Civility']
        shippping_civility_id = getcivility_Id(session, shippping_shortCivility)
        shippping_partner_name = record['ShippingAddress']['FirstName'].title() + " " + record['ShippingAddress']['LastName'].title()
        shipping_values = {
                      'title' : shippping_civility_id,
                      'type' : 'delivery',
                      'cdis_Id': record['OrderNumber'],
                      'name' : shippping_partner_name,
                      #'mobile' :record['Customer']['MobilePhone'],
                      'street': record['ShippingAddress']['Street'],
                      'zip': record['ShippingAddress']['ZipCode'],
                      'city': record['ShippingAddress']['City'],
                      'country_id': country_Id,
                      'customer': True,
                      'parent_id': partner_customer.id,
                    }
        partner_shipping = session.env['res.partner'].create(shipping_values)

    else:
        #le client existe déjà
        _logger.info('le client exist deja')
        partner_customer = pids
        billing_shortCivility = record['Customer']['Civility']
        billing_civility_id = getcivility_Id(session, billing_shortCivility)
        billing_partner_name = record['BillingAddress']['FirstName'].title() + " " + record['BillingAddress']['LastName'].title()
        billing_values = {
                      'title' : billing_civility_id,
                      'type' : 'invoice',
                      'cdis_Id': record['OrderNumber'],
                      'name' : billing_partner_name,
                      #'mobile' :record['Customer']['MobilePhone'],
                      'street': record['BillingAddress']['Street'],
                      'zip': record['BillingAddress']['ZipCode'],
                      'city': record['BillingAddress']['City'],
                      'country_id': country_Id,
                      'customer': True,
                      'parent_id':pids.id
                    }
        partner_billing = session.env['res.partner'].create(billing_values)

       #creation du respartner shipping
        shippping_shortCivility = record['Customer']['Civility']
        shippping_civility_id = getcivility_Id(session, shippping_shortCivility)
        shippping_partner_name = record['ShippingAddress']['FirstName'].title() + " " + record['ShippingAddress']['LastName'].title()
        shipping_values = {
                      'title' : shippping_civility_id,
                      'type' : 'delivery',
                      'cdis_Id': record['OrderNumber'],
                      'name' : shippping_partner_name,
                      #'mobile' :record['Customer']['MobilePhone'],
                      'street': record['ShippingAddress']['Street'],
                      'zip': record['ShippingAddress']['ZipCode'],
                      'city': record['ShippingAddress']['City'],
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

