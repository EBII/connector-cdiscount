from zeep import Client
from zeep.wsse.username import UsernameToken
import sys
import datetime as date
import xmltodict as xd
import json
# message = "[USAGE] getSales.py <username> <password> N \
#            N=0 preprod N=1 prod "
# username = ''
# password = ''
# mode = 0
# if len(sys.argv) == 4:
#     username = sys.argv[1]
#     password = sys.argv[2]
#     mode = int(sys.argv[3])
#     if mode != 0 and mode != 1:
#         sys.exit(message)
# else:
#     sys.exit(message)
#
#
# #convert sample en dict to return for dev
#
# with open('sample.xml','r') as f:
#     d = xd.parse(f)
# sys.exit(d)

def do_the_job(username, password, mode ):

    #print username, password, mode

    # #constantes URL
    # sts_preprod = 'https://sts.preprod-cdiscount.com/users/httpIssue.svc/?realm=https://wsvc.preprod-cdiscount.com/MarketplaceAPIService.svc'
    # api_preprod = 'https://wsvc.preprod-cdiscount.com/MarketplaceAPIService.svc'
    # sts_prod = 'https://sts.cdiscount.com/users/httpIssue.svc/?realm=https://wsvc.cdiscount.com/MarketplaceAPIService.svc'
    # api_prod = 'https://wsvc.cdiscount.com/MarketplaceAPIService.svc'
    # wsdl = 'https://wsvc.cdiscount.com/MarketplaceAPIService.svc?wsdl'
    #
    # #client = Client(wsdl=wsdl)
    # # selon type on appel prod ou preprod
    # if (mode):
    #     sts = sts_preprod
    #     api = api_preprod
    # else:
    #     sts= sts_prod
    #     api= api_prod
    #
    # username += "-api" #ajouter -api au identifiants vendeur
    # password += "-api"
    #
    # #print username, password
    #
    # client = Client(
    #                  sts,
    #                  wsse=UsernameToken('username', 'password', use_digest=True)) # use_digest=True encode en base 64
    # # filtre de requete seulement les ventes en attente d'acceptation
    # OrderFilter = { 'OrderStateEnum': 'WaitingForSellerAcceptation'}
    #
    # list_of_sale = client.service.GetOrderList( {'orderFilter': OrderFilter})
    #
    # #voir les listes de ventes
    # print "liste of sales : " +list_of_sale
    #
    # #on parse le xml
    # h_list_of_sale = xd.parse(list_of_sale)
    #
    # #On peut ecrire le fichier
    # adate = date.today()
    # with open('sales_'+adate+'.txt', 'wb') as fh:
    #     json.dump(h_list_of_sale, fh)
    namespaces = {
        'http://schemas.xmlsoap.org/soap/envelope/': None,  # skip this namespace
        'http://www.cdiscount.com': None,  # collapse "http://a.com/" -> "ns_a"
        'http://www.w3.org/2001/XMLSchema-instance': None,  # collapse "http://a.com/" -> "ns_a"
        'http://schemas.datacontract.org/2004/07/Cdiscount.Framework.Core.Communication.Messages': None,
    # collapse "http://a.com/" -> "ns_a"
    }
    with open('tests/sample.xml', 'r') as f:
        d = xd.parse(f, process_namespaces=True, namespaces=namespaces)

    return d #h_list_of_sale
