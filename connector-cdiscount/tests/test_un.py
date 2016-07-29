# -*- coding: utf-8 -*-
import unittest
from .. import sale

class TestalaCon(unittest.TestCase):

    def test_somme(self):
        a=2
        b=3
        c= a+b
        print "COUCOUCOCUOCUCOUCOCU "+str(c)
        self.assertEquals(c,5)


class TestConnector(unittest.TestCase):

    def create_attachment(self):
        print "zzzzzzzzzzzzzzzzzooooooooooooooooooooobbbbbbbbbbbbbb"
        cdiscountAdapter = sale.CdiscountAdapter().search_read()
        print str(cdiscountAdapter)
        sale.SaleOrderBatchImport.sale_order_import_batch()
