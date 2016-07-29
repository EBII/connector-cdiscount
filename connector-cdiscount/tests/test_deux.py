# -*- coding: utf-8 -*-
import unittest
from .. import sale



class TestConnector(unittest.TestCase):

    def create_attachment(self):
        print "zzzzzzzzzzzzzzzzzooooooooooooooooooooobbbbbbbbbbbbbb"
        cdiscountAdapter = sale.CdiscountAdapter().search_read()
        print str(cdiscountAdapter)
        sale.SaleOrderBatchImport.sale_order_import_batch()
