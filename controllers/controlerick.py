from asyncio.log import logger
import base64
import json
from logging import Logger
import sys
import requests
from .main import ERROR_TYPE_DATA_ERROR, ERROR_TYPE_DATA_NOT_FOUND, ERROR_TYPE_MANDATORY_PARAMS, check_valid_secret, invalid_response_json, valid_response_json
import werkzeug.wrappers 
from odoo import  api, models, fields, _
from odoo import http, _, exceptions
import io
import xlsxwriter  
from odoo.http import Response, request
from odoo.tools.translate import _
from odoo import http  
import os
from uuid import uuid4 
from datetime import datetime, timedelta, date 
from zlib import crc32


class AlgoritmaPembelianResApi(http.Controller):
     
    @http.route(['/api/algoritma_transaction_get/'], auth='public',type='http',  methods=['GET'], csrf=False)
    def hello  (self, **kw):  
        contact_user = http.request.env['res.partner'].sudo().search([('id','=',12)])
        contact_user.write({'name':'Ready Matt'})
        return kw  
    @http.route('/api/core/token', methods=['POST'],type='http',auth='public', csrf=False)
    def gettoken  (self, **kw): 
        info=''
        mandatory_header = [ 
            'ClientID',
            'SecretKey', 
        ]
        
        header_fields = [] ##ini tuh untuk menampung mandatory field yang gak disupport sama user
        dict_draftwo ={}
        data_draftwo =[]
        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False):
                header_fields.append(mandatory_field)  
        if len(header_fields) > 0:
            info = "B2B ODOO MAM missing required data in header %s" %str(header_fields) 
            dict_draftwo={     
                        'Token': '',
                        'Status':'false', 
                        'Message':info
                        }
            data_draftwo.append(dict_draftwo)  
        else:
            clientid = kw.get('ClientID')
            secretkey = kw.get('SecretKey')
            if(clientid != 'X2K02YI0P1Y7LF6HXZYPDQ' or secretkey != '8fMF8A5Q'):
                info = 'wrong client id or secret key'
                dict_draftwo={     
                            'Token': '',
                            'Status':'false', 
                            'Message':info
                            }
                data_draftwo.append(dict_draftwo)
            else: 
                info = 'succeed v.1'
                tokent_history = http.request.env['tl.ms.tokenhistory'].sudo().search([('clientid','=',clientid),('isactive','=',True),('expireddate','>=',date.today())]) 
                if(tokent_history.id == False):
                    tokent_history.create({'clientid':clientid})
                    tokent_history = http.request.env['tl.ms.tokenhistory'].sudo().search([('clientid','=',clientid),('isactive','=',True)]) 
                    info = 'succeed v.2'
                # print(tokent_history,'ass') 
             
                dict_draftwo={     
                            'Token': tokent_history.token,
                            'Status':'true', 
                            'Message':info  
                            }
                data_draftwo.append(dict_draftwo)

        kw=json.dumps(data_draftwo) 
        return kw 
 

 
    # @http.route('/api/algoritma_transaction_get2/', methods=['POST'],type='http',auth='public', csrf=False)
    @http.route('/api/algoritma_transaction_get2/', methods=['POST'],type='http',auth='public', csrf=False)
    @check_valid_secret
    def hello2  (self, **kw):   
        dwoid=''
        dict_draftwo ={}
        data_draftwo =[]
        mandatory_header = [  
            'dwoid', 
            'clientid', 
        ]
        draftwo=''
        header_fields = [] ##ini tuh untuk menampun mandatory field yang gak disupport sama user
        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False):
                header_fields.append(mandatory_field) 
            
        if len(header_fields) > 0: 
            info = "B2B ODOO MAM missing required data in header %s" %str(header_fields) 
            dict_draftwo={
                        'Status':'false', 
                        'Message':info
                        }
            data_draftwo.append(dict_draftwo)   
        else:    
            dwoid = kw.get('dwoid')	 
            clientid=kw.get('clientid')
            if(dwoid == ''):
                info = 'wrong dwoid'
                dict_draftwo={      
                            'dwoid': dwoid,
                            'Status':'false', 
                            'Message':info
                            }
                data_draftwo.append(dict_draftwo)
            elif(clientid ==''):
                info = 'wrong clientid'
                dict_draftwo={      
                            'clientid': clientid,
                            'Status':'false', 
                            'Message':info
                            }
                data_draftwo.append(dict_draftwo)
            else:
                tokent_history = http.request.env['tl.ms.tokenhistory'].sudo().search([('clientid','=',clientid),('isactive','=',True),('expireddate','>=',date.today())]) 
                
                draftwo = http.request.env['tl.tr.draftwo'].sudo().search([('dwoid','=',dwoid)]) 
                if(draftwo.id == False):
                    info = 'no data with dwoid'+dwoid
                    dict_draftwo={      
                                'dwoid': dwoid,
                                'Status':'false', 
                                'Message':info
                                }
                    data_draftwo.append(dict_draftwo)  
                elif not tokent_history.id:
                    info = 'client id not found or token expired '+clientid
                    dict_draftwo={      
                                'dwoid': dwoid,
                                'Status':'false', 
                                'Message':info
                                }
                    data_draftwo.append(dict_draftwo)  
                else: 
                    for h in draftwo: 
                        dict_draftwo={     
                                    'id': h.id,
                                    'dwoid':h.dwoid, 
                                    'wono':h.wono, 
                                    'invoiceno':h.invoiceno, 
                                    'customername':h.customerid.name, 
                                    'stage':h.stage, 
                                    'brand':h.qi_brand, 
                                    'locationfrom':h.qi_locationfrom, 
                                    'locationto':h.qi_locationto, 
                                    'salesprice':h.qi_salesprice,    
                                }
                        data_draftwo.append(dict_draftwo) 
        kw=json.dumps(data_draftwo) 
         
        return kw  
    @http.route('/api/master/customerlocation/', methods=['POST'],type='http',auth='public', csrf=False)
    @check_valid_secret
    def getcustomerlocation  (self, **kw):    
        dict ={}
        data =[]
        mandatory_header = [   
            'clientid', 
        ]
        customerlocation=''
        header_fields = [] ##ini tuh untuk menampun mandatory field yang gak disupport sama user
        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False):
                header_fields.append(mandatory_field) 
            
        if len(header_fields) > 0: 
            info = "B2B ODOO MAM missing required data in header %s" %str(header_fields) 
            dict={
                        'Status':'false', 
                        'Message':info
                        }
            data.append(dict)   
        else:     
            clientid=kw.get('clientid')  
            if(clientid ==''):
                info = 'wrong clientid'
                dict={      
                            'clientid': clientid,
                            'Status':'false', 
                            'Message':info
                            }
                data.append(dict)
            else:
                tokent_history = http.request.env['tl.ms.tokenhistory'].sudo().search([('clientid','=',clientid),('isactive','=',True),('expireddate','>=',date.today())]) 
                if not tokent_history.id:
                    info = 'client id not found or token expired '+clientid
                    dict={       
                                'Status':'false', 
                                'Message':info
                                }
                    data.append(dict)  
                else:
                    customerlocation = http.request.env['tl.ms.customerlocation'].sudo().search([('id','>',0)]) 
                    for row in customerlocation: 
                        for h in row: 
                            if(h.id == False):
                                info = 'no data Customer location'
                                dict={       
                                            'Status':'false', 
                                            'Message':info
                                            }
                                data.append(dict)    
                            else:  
                                dict={     
                                            'id': h.id,
                                            'name':h.locationname, 
                                            'customer':h.customerid.name,  
                                        }
                                data.append(dict) 
        kw=json.dumps(data) 
         
        return kw  
    @http.route('/api/master/customer/', methods=['POST'],type='http',auth='public', csrf=False)
    @check_valid_secret
    def getcustomer  (self, **kw):    
        dict ={}
        data =[]
        mandatory_header = [   
            'clientid', 
        ]
        driver=''
        header_fields = [] ##ini tuh untuk menampun mandatory field yang gak disupport sama user
        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False):
                header_fields.append(mandatory_field) 
            
        if len(header_fields) > 0: 
            info = "B2B ODOO MAM missing required data in header %s" %str(header_fields) 
            dict={
                        'Status':'false', 
                        'Message':info
                        }
            data.append(dict)   
        else:     
            clientid=kw.get('clientid')  
            if(clientid ==''):
                info = 'wrong clientid'
                dict={      
                            'clientid': clientid,
                            'Status':'false', 
                            'Message':info
                            }
                data.append(dict)
            else:
                tokent_history = http.request.env['tl.ms.tokenhistory'].sudo().search([('clientid','=',clientid),('isactive','=',True),('expireddate','>=',date.today())]) 
                if not tokent_history.id:
                    info = 'client id not found or token expired '+clientid
                    dict={       
                                'Status':'false', 
                                'Message':info
                                }
                    data.append(dict)  
                else:
                    driver = http.request.env['res.partner'].sudo().search([('is_logistic_customer','=',True),('is_company','=',True)]) 
                    for row in driver: 
                        for h in row: 
                            if(h.id == False):
                                info = 'no data Customer'
                                dict={       
                                            'Status':'false', 
                                            'Message':info
                                            }
                                data.append(dict)    
                            else: 
                                url = 'exis.tunasgroup.com/web/image?model=res.partner&id=#IDCUSTOMER#&field=image_128'
                                url = url.replace("#IDCUSTOMER#", str(h.id))

                                dict={     
                                            'id': h.id,
                                            'name':h.name, 
                                            'title':h.title.name, 
                                            'active':h.active, 
                                            'type':h.type, 
                                            'street':h.street, 
                                            'street2':h.street2, 
                                            'zip':h.zip, 
                                            'country':h.country_id.name,  
                                            'city':h.city, 
                                            'state':h.state_id.name, 
                                            'phone':h.phone, 
                                            'mobile':h.mobile, 
                                            'email':h.email_normalized,   
                                            'profilephoto': str(h.image_128)
                                        }
                                data.append(dict) 
        kw=json.dumps(data) 
         
        return kw  
    @http.route('/api/master/driver/', methods=['POST'],type='http',auth='public', csrf=False)
    @check_valid_secret
    def getdriver  (self, **kw):    
        dict ={}
        data =[]
        mandatory_header = [   
            'clientid', 
        ]
        driver=''
        header_fields = [] ##ini tuh untuk menampun mandatory field yang gak disupport sama user
        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False):
                header_fields.append(mandatory_field) 
            
        if len(header_fields) > 0: 
            info = "B2B ODOO MAM missing required data in header %s" %str(header_fields) 
            dict={
                        'Status':'false', 
                        'Message':info
                        }
            data.append(dict)   
        else:     
            clientid=kw.get('clientid')  
            if(clientid ==''):
                info = 'wrong clientid'
                dict={      
                            'clientid': clientid,
                            'Status':'false', 
                            'Message':info
                            }
                data.append(dict)
            else:
                tokent_history = http.request.env['tl.ms.tokenhistory'].sudo().search([('clientid','=',clientid),('isactive','=',True),('expireddate','>=',date.today())]) 
                if not tokent_history.id:
                    info = 'client id not found or token expired '+clientid
                    dict={       
                                'Status':'false', 
                                'Message':info
                                }
                    data.append(dict)  
                else:
                    driver = http.request.env['res.partner'].sudo().search([('is_driver','=',True)]) 
                    for row in driver: 
                        for h in row: 
                            if(h.id == False):
                                info = 'no data driver'
                                dict={       
                                            'Status':'false', 
                                            'Message':info
                                            }
                                data.append(dict)    
                            else: 
                                url = 'exis.tunasgroup.com/web/image?model=res.partner&id=#IDDRIVER#&field=image_128'
                                url = url.replace("#IDDRIVER#", str(h.id))

                                dict={     
                                            'id': h.id,
                                            'name':h.name, 
                                            'title':h.title.name, 
                                            'active':h.active, 
                                            'type':h.type, 
                                            'city':h.city, 
                                            'state':h.state_id.name, 
                                            'phone':h.phone, 
                                            'mobile':h.mobile, 
                                            'email':h.email_normalized, 
                                            'drivertype':h.drivertype, 
                                            'driveralias':h.driveralias, 
                                            'korlap':h.korlap.name,     
                                            'cara_decode_profilephoto':'contoh decode ke image https://codebeautify.org/base64-to-image-converter',    
                                            'profilephoto': str(h.image_128).replace("b'","").replace("'","") 
                                        }
                                data.append(dict) 
        kw=json.dumps(data) 
         
        return kw  
   
    @http.route('/api/algoritma_transaction_post/', methods=['POST'], type='http',auth='none', csrf=False)
    @check_valid_secret
    def b2b_ibes_payment(self, **post):
        end_point = "/api/b2b/ibes/v1/payment/add"
        message = []
        method = 'post'
        mandatory_header = [
            'PaymentDate',
            'PaymentDocumentNumber',
            'PaymentLine',
        ]
        header_fields = []
        for mandatory_field in mandatory_header:
            if not post.get(mandatory_field,False):
                header_fields.append(mandatory_field)
        if len(header_fields) > 0:
            info = "B2B IBES missing required data in header %s" %str(header_fields) 
         
        ibes_payment_no = post.get('PaymentDocumentNumber')
        ibes_payment_date = post.get('PaymentDate')
        validation_status = 1
        # Initiate Mandatory params for line
        mandatory_fields = [
            'BranchID',
            'IbesDocumentNumber',
            'DocumentNumber',
            'PartnerCode',
            'PartnerAccountNumber',
            'Amount',
        ]
        for data in post.get('PaymentLine'):
            line_fields = []
            for mandatory_field in mandatory_fields:
                if not data.get(mandatory_field,False):
                    line_fields.append(mandatory_field)
            if len(line_fields) > 0:
                validation_status = 0
                info = "B2B IBES missing required data in line %s" %str(line_fields)
                logger.error(info)
                message.append({'transaction_id':ibes_payment_no,'error':ERROR_TYPE_MANDATORY_PARAMS,'info':info})
                continue
        
            branch_id = data.get('BranchID')
            ibes_document_number = data.get('IbesDocumentNumber')
            document_number = data.get('DocumentNumber')
            partner_code = data.get('PartnerCode')
            partner_account_number = data.get('PartnerAccountNumber')
            amount = data.get('Amount')

            # Search transaction type based on 3 first of document number 
            model = False
            name_field = 'name'
            amount_field = 'amount'
            paid_state = 'posted'
            if document_number[:3] == 'PV/':
                model = 'wtc.account.voucher'
                name_field = 'number'
            elif document_number[:3] == 'BT/':
                model = 'wtc.bank.transfer'
                paid_state = 'approved'
            elif document_number[:3] == 'AVP':
                model = 'wtc.advance.payment'
            elif document_number[:3] == 'STL':
                model = 'wtc.settlement'
                amount_field = 'amount_gap'
            if not model:
                validation_status = 0
                info = "B2B IBES Invalid DocumentNumber type for %s in line params" %document_number
                logger.error(info)
                message.append({'transaction_id':document_number,'error':ERROR_TYPE_DATA_ERROR,'info':info})
                continue
            
            # Search transaction
            document_obj = request.env[model].sudo().search([
                (name_field,'=',document_number),
                ('ibes_reference_number','=',ibes_document_number)
            ],limit=1)
            if not document_obj:
                validation_status = 0
                info = "B2B IBES Document not found for %s in line params" %ibes_document_number
                logger.error(info)
                message.append({'transaction_id':document_number,'error':ERROR_TYPE_DATA_NOT_FOUND,'info':info})
                continue
            
            # Check Partner Code
            if document_obj.partner_bank_id.partner_id.default_code != partner_code:
                validation_status = 0
                info = "B2B IBES Invalid PartnerCode %s for %s in line params" %(partner_code,ibes_document_number)
                logger.error(info)
                message.append({'transaction_id':document_number,'error':ERROR_TYPE_DATA_NOT_FOUND,'info':info})
                continue

            # Check Partner Account Number
            if document_obj.partner_bank_id.account_number != partner_account_number:
                validation_status = 0
                info = "B2B IBES Invalid PartnerAccountNumber %s for %s in line params" %(partner_account_number,ibes_document_number)
                logger.error(info)
                message.append({'transaction_id':document_number,'error':ERROR_TYPE_DATA_NOT_FOUND,'info':info})
                continue
            
            # Check amount
            document_data = document_obj.read()[0]
            document_amount = document_data.get(amount_field,0)
            if document_amount != amount:
                validation_status = 0
                differences = document_amount-amount
                info = "B2B IBES %s unbalance amount for %s in line params" %(differences,ibes_document_number)
                logger.error(info)
                message.append({'transaction_id':document_number,'error':ERROR_TYPE_DATA_ERROR,'info':info})
                continue

            # Check if payment already paid
            if document_obj.state == paid_state:
                # Write payment number if ibes payment number is empty
                if not document_obj.ibes_payment_number:
                    document_obj.suspend_security().write({
                        'ibes_payment_number':ibes_payment_no,
                    })
                info = 'B2B IBES Already Paid'
                message.append({'transaction_id':document_number,'error':False,'info':info})
                continue
            
            # Confirm payment and write IBEST payment number
            try:
                ibes_partner = request.env['res.users'].sudo().search([('name','=','admin')],limit=1)
                document_obj.action_confirm_payment_from_ibes()
                document_obj.suspend_security().write({
                    'ibes_payment_number':ibes_payment_no,
                    'confirm_uid':ibes_partner.id,
                    'confirm_date':datetime.now(),
                })
                info = 'B2B IBES Payment Success'
                message.append({'transaction_id':document_number,'error':False,'info':info})
                continue
            except Exception as e:
                validation_status = 0
                info = "B2B IBES %s" %(str(e))
                logger.error(info)
                message.append({'transaction_id':document_number,'error':ERROR_TYPE_DATA_ERROR,'info':info})
                continue
        
        return valid_response_json(message,ibes_payment_no,True,'incoming',end_point,method,post,validation_status)


# class AlgoritmaPembelianResApi(http.Controller):
#     @http.route(['/api/algoritma_transaction_get/'], type='http', auth='public', methods=['GET'], csrf=False)
#     def algoritma_transaction_resapi_get(self, **params):
#         algoritma_transaction= http.request.env['tl.tr.draftwo'].sudo().search([])
#         dict_algoritma_transaction ={}
#         data_algoritma_transaction =[]
#         # for h in algoritma_transaction:
            
#         #     # dict_draftwo =  {}
#         #     # detail_draftwo = []
#         #     # dict_detail_product = {}
#         #     # detail_product =[]
#         #     # for b in h.PIC:
#         #     #     dict_draftwo = {'id':b.id, 'name': b.name}
#         #     #     detail_draftwo.append((dict_draftwo))
#         #     # for p in h.algoritma_transaction_ids:
#         #     #     dict_detail_product = {'product_id': p.product_id.display_name, 'description':p.description, 'quantity':p.quantity, 'uom_id': p.uom_id.name, 'price': p.price, 'sub_total': p.sub_total}
#         #     #     detail_product.append(dict_detail_product)
#         #     dict_algoritma_transaction={     
#         #                             # 'id': h.id,
#         #                             # 'dwoid':h.dwoid, 
#         #                             # 'wono':h.wono, 
#         #                             # 'invoiceno':h.invoiceno, 
#         #                             # 'customername':h.customerid.name, 
#         #                             # 'stage':h.stage, 
#         #                             # 'brand':h.qi_brand, 
#         #                             # 'locationfrom':h.qi_locationfrom, 
#         #                             # 'locationto':h.qi_locationto, 
#         #                             # 'salesprice':h.qi_salesprice, 
#         #                             'salesprice':'mmk', 
#         #                             # 'brand_ids':detail_draftwo,  
#         #                             # 'algoritma_transaction_ids': detail_product 
#         #                             }
             
#         # data_algoritma_transaction.append(dict_algoritma_transaction)

#         data={'status': 200,'message': 'success', 'response': 'asu'}
#         # data={'status': 200,'message': 'success', 'response': data_algoritma_transaction}
        
#         return werkzeug.wrappers.response(
#             status=200,
#             content_type='application/json; charset=utf-8',
#             response=json.dumps(data)
#             )
#         # try: 
#         #     return werkzeug.wrappers.response(
#         #         status=200,
#         #         content_type='application/json; charset=utf-8',
#         #         response=json.dumps(data)
#         #         ) 
#         # except: 
#         #     # return werkzeug.wrappers.response(
#         #     #     status=400,
#         #     #     content_type='application/json; charset=utf-8',
#         #     #     headers=[('Access-Control-Allow-Origin', '*')],
#         #     #     response=json.dumps({
#         #     #         'error' : 'Error',
#         #     #         'error_description': 'Error Description',
#         #     #     })
#         #     # )






