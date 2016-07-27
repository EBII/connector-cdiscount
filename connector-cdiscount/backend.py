import openerp.addons.connector.backend as backend
import openerp.addons.connector_ecommerce.GenericAdapter as GenericAdapter


cdiscount = backend.Backend('cdiscount')
cdiscountActuel = backend.Backend(parent=cdiscount, version='01/08/2016')
