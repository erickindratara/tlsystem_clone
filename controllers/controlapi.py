
from odoo import http  
# # import xmlrpclib
# from xmlrpc import client
# url = 'https://demo5.odoo.com'
# db = 'demo5'
# # url = 'https://exisa.tunasgroup.com:80'
# # db = 'tlsystemdb_devo'
# # username = 'posgre'
# # password = '1'
# username = 'admin'
# password = 'admin'
# common = client.ServerProxy('{}/xmlrpc/2/common'.format(url)) 
# output = common.methodHelp()
# print(output)
# # # python testrpc2.py 

# import xmlrpc.client
# info = xmlrpc.client.ServerProxy('https://exis.tunasgroup.com:80/').start()
# url, db, username, password = info['host'], info['database'], info['user'], info['password'] 
url = 'http://exis.tunasgroup.com'
# url = 'http://127.0.0.1/'
# db = 'tlsystemdb_devo'
# username = '081807902390'
# password = 'eee547be6bd131202d22fcc20d98d431e4470574' 
import xmlrpc.client

common = xmlrpc.client.ServerProxy('%s/xmlrpc/2/common' % url)
  
# defaultcus = http.request.env['res.users'].sudo().search([('id','!=',1)]) 
# print(defaultcus)
version = common.version()
a=      "                                                                                                          \n "
a=a+    "           ███████   ████████   ██     ███████   ██     ██           ██         ████████████              \n "
a=a+    "           ██        ██    ██   ██    ███        ██    ██            ██              ██                   \n "
a=a+    "           ██        ██    ██   ██    ██         ██   ██             ██              ██                   \n "
a=a+    "           █████     ██████     ██    ██         ██ ███              ██              ██                   \n "
a=a+    "           ██        ██  ██     ██    ██         ██   ██             ██              ██                   \n "
a=a+    "           ██        ██   ██    ██    ███        ██    ██            ██              ██                   \n "
a=a+    "           ███████   ██    ██   ██     ███████   ██     ██    ██     ██    ██        ██       2022        \n "
a=a+    "                                                                                                          \n "
print(a)
print("details...", version)