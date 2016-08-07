# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Eric BOUHANA <eric@ebii.fr>
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Cdiscount Marketplace Connector',
    'version': '8.0.1.0',
    'category': 'Connector',
    'depends': ['connector',],
    'author': 'Akretion, Eric Bouhana, Sebastien Beau',
    'license': 'AGPL-3',
    'description': """
           Connector pour la marketplace de Cdiscount

           Connect Odoo to Cdiscount Marketplace.

           Features:
                    WORK in Progress
           """ ,
    'depends': ['connector'],
    'data': [   'views/connector_cdiscount_view.xml',
                'views/connector_cdiscount_menu.xml',
             ],
    'demo': ['demo/cdiscount.backend.xml'],
    'installable': True,
    'application': True,
}
