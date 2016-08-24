# -*- coding: utf-8 -*-
from openerp import models, fields, api


class res_partner(models.Model) :
    """ Inherits partner and adds contract information in the partner form """
    _inherit = 'res.partner'
    cdis_Id = fields.Char("id cdiscount")
