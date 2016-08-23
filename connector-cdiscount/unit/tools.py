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
    pids = session.env['res.partner'].search([('cdis_Id', 'ilike', client_id)])
    _logger.info('create contact civility or get id:' + record['Order']['Customer']['Civility'])

    if len(pids) !=1 :
        # le client nexiste pas
        shortCivility = record['Order']['Customer']['Civility']
        civility_id = getcivility_Id(session, shortCivility)
        partner_name = record['Order']['Customer']['FirstName'].title() + " " + record['Order']['Customer']['LastName'].title()
        partner_values = {
                      'title' : civility_id,
                      'cdis_Id': record['Order']['Customer']['CustomerId'],
                      'name' : partner_name,
                      'mobile' :record['Order']['Customer']['MobilePhone'],
                      'street': record['Order']['ShippingAddress']['Street'],
                      'zip': record['Order']['ShippingAddress']['ZipCode'],
                      'city': record['Order']['ShippingAddress']['City'],
                      'country_id': country_Id,
                      'customer': True,
                    }
        partner_Id = session.env['res.partner'].create(partner_values)
    else:
        #le client existe déjà
        _logger.info('le client exist deja')
        partner_Id = pids
    return partner_Id.id


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

