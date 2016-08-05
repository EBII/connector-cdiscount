# -*- coding: utf-8 -*-
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
import openerp.addons.connector.backend as backend

cdiscount = backend.Backend('cdiscount')
cdiscountActuel = backend.Backend(parent=cdiscount, version='01/08/2016')

