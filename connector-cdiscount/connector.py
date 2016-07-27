from openerp import models, fields
from openerp.addons.connector.connector import ConnectorEnvironment
from openerp.addons.connector.checkpoint import checkpoint

class CdiscountBinding(models.AbstractModel):
    _name       = 'cdiscount.binding'
    _inherit    = 'external.binding'
    _description = 'Cdiscount Binding (abstract)'

    # 'openerp_id': openerp-side id must be declared in concrete model
    backend_id = fields.Many2one(
        comodel_name='cdiscount.backend',
        string='Cdiscount Backend',
        required=True,
        ondelete='restrict',
    )
    # fields.char because 0 is a valid cdiscount ID
    cdiscount_id = fields.Char(string='ID in the Cdiscount Machine',
                            select=True)


def get_environment(session, model_name, backend_id):
    """ Create an environment to work with. """
    backend_record = session.env['cdiscount.backend'].browse(backend_id)
    env = ConnectorEnvironment(backend_record, session, model_name)
    lang = backend_record.default_lang_id
    lang_code = lang.code if lang else 'en_US'
    if lang_code == session.context.get('lang'):
        return env
    else:
        with env.session.change_context(lang=lang_code):
            return env

def sale_list_import(self):

     # appeler l'adaptateur qui renvoi une liste de sale_order en dictionnaire

        sale_list = {
            "s:Envelope": {
              "-xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/",
              "s:Body": {
                "GetOrderListResponse": {
                  "-xmlns": "http://www.cdiscount.com",
                  "GetOrderListResult": {
                    "-xmlns:i": "http://www.w3.org/2001/XMLSchema-instance",
                    "ErrorMessage": {
                      "-i:nil": "true",
                      "-xmlns": "http://schemas.datacontract.org/2004/07/Cdiscount.Framework.Core.Communication.Messages"
                    },
                    "OperationSuccess": {
                      "-xmlns": "http://schemas.datacontract.org/2004/07/Cdiscount.Framework.Core.Communication.Messages",
                      "#text": "true"
                    },
                    "SellerLogin": "login",
                    "TokenId": "???",
                    "OrderList": {
                      "Order": {
                        "ArchiveParcelList": "false",
                        "BillingAddress": {
                          "Address1": { "-i:nil": "true" },
                          "Address2": { "-i:nil": "true" },
                          "City": "BORDEAUX",
                          "Civility": "MISS",
                          "CompanyName": { "-i:nil": "true" },
                          "Country": "FR",
                          "FirstName": "VALERIE",
                          "LastName": "MUGNIER",
                          "Street": "18 AVENUE D EYSINES",
                          "ZipCode": "33200"
                        },
                        "CreationDate": "2011-07-26T12:38:31.35",
                        "Customer": {
                          "Civility": "MISS",
                          "CustomerId": "144a7211e0f420a43c208ec6706b1756",
                          "FirstName": "VALERIE",
                          "LastName": "MUGNIER",
                          "MobilePhone": "0609046706"
                        },
                        "HasClaims": "false",
                        "InitialTotalAmount": "3.7",
                        "InitialTotalShippingChargesAmount": "2.5",
                        "LastUpdatedDate": "2011-10-21T07:18:14.327",
                        "ModifiedDate": "2011-07-26T12:39:43.21",
                        "Offer": { "-i:nil": "true" },
                        "OrderLineList": {
                          "OrderLine": {
                            "AcceptationState": "ShippedBySeller",
                            "CategoryCode": "06010701",
                            "DeliveryDateMax": "2011-07-31T12:38:07.967",
                            "DeliveryDateMin": "2011-07-28T12:38:07.967",
                            "HasClaim": "false",
                            "Name": { "-i:nil": "true" },
                            "ProductCondition": "New",
                            "ProductEan": "0123456789123",
                            "ProductId": "3275054001106",
                            "PurchasePrice": "1.2",
                            "Quantity": "1",
                            "RowId": "0",
                            "SellerProductId": "REF3275054001",
                            "ShippingDateMax": "0001-01-01T00:00:00",
                            "ShippingDateMin": "0001-01-01T00:00:00",
                            "Sku": "3275054001106",
                            "SkuParent": { "-i:nil": "true" },
                            "UnitAdditionalShippingCharges": "0.15",
                            "UnitShippingCharges": "2.5"
                          }
                        },
                        "OrderNumber": "1107261238TV3HA",
                        "OrderState": "Shipped",
                        "ShippedTotalAmount": "0",
                        "ShippedTotalShippingCharges": "0",
                        "ShippingAddress": {
                          "Address1": { "-i:nil": "true" },
                          "Address2": { "-i:nil": "true" },
                          "City": "BORDEAUX",
                          "Civility": "MISS",
                          "CompanyName": { "-i:nil": "true" },
                          "Country": "FR",
                          "County": "N/A",
                          "FirstName": "VALERIE",
                          "LastName": "MUGNIER",
                          "RelayId": { "-i:nil": "true" },
                          "Street": "18 AVENUE D EYSINES",
                          "ZipCode": "33200"
                        },
                        "ShippingCode": "STD",
                        "SiteCommissionPromisedAmount": "0",
                        "SiteCommissionShippedAmount": "0",
                        "SiteCommissionValidatedAmount": "0",
                        "Status": "Completed",
                        "ValidatedTotalAmount": "0",
                        "ValidatedTotalShippingCharges": "0",
                        "ValidationStatus": "None",
                        "Corporation": {
                          "CorporationId": "1",
                          "CorporationName": "Cdiscount",
                          "BusinessUnitId": "1",
                          "IsMarketPlaceActive": "true",
                          "CorporationCode": "CDSB2C"
                        }
                      }
                    }
                  }
                }
              }
            }
      }
        return sale_list
