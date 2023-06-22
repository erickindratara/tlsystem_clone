 
from .main import ERROR_TYPE_DATA_ERROR, ERROR_TYPE_DATA_NOT_FOUND, ERROR_TYPE_MANDATORY_PARAMS, check_valid_secret, invalid_response_json, valid_response_json
from odoo import http, _, exceptions 
import json
from datetime import datetime, timedelta, date 

 
from odoo.exceptions import UserError, ValidationError   
from Crypto.Cipher import AES
from secrets import token_bytes 
from base64 import b64encode 
from base64 import b64decode
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Crypto.Random import get_random_bytes 





class mobilegettoken(http.Controller):

    @http.route('/api/verifikasitoken/', methods=['POST'],type='http',auth='public', csrf=False)
    def verifytoken  (self, **kw):   
        dict_tok={}
        data_tok =[]
        mandatory_header = ['clientid','secretkey','userid','password',]
        
        draftwo=''
        header_fields = [] ##ini tuh untuk menampun mandatory field yang gak disupport sama user
        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False):
                header_fields.append(mandatory_field) 
            
        if len(header_fields) > 0: 
            info    = "B2B ODOO MAM missing required data in header %s" %str(header_fields) 
            dict_tok={'Status':'false','message':info}
        else: 	 
            clientid    =kw.get('clientid') ;   secretkey   =kw.get('secretkey')
            userid      =kw.get('userid')   ;   password    =kw.get('password')
            if  (clientid   ==''                ):info = 'empty clientid'   ; dict_tok={'code':400,'message':info}; data_tok.append(dict_tok)
            elif(secretkey  ==''                ):info = 'empty secretkey'  ; dict_tok={'code':401,'message':info}; data_tok.append(dict_tok)
            elif(userid     ==''                ):info = 'empty userid'     ; dict_tok={'code':402,'message':info}; data_tok.append(dict_tok)
            elif(password   ==''                ):info = 'empty password'   ; dict_tok={'code':403,'message':info}; data_tok.append(dict_tok)
            elif(clientid   !='DRIVERMAM'       ):info = 'wrong clientid'   ; dict_tok={'code':404,'message':info}; data_tok.append(dict_tok)
            elif(secretkey  !='KATAKUNCIRAHASIA'):info = 'wrong secretkey'  ; dict_tok={'code':405,'message':info}; data_tok.append(dict_tok)
            else: 
                resuser         = http.request.env['res.users'].sudo().search([('login','=',userid)])
                partnerid       = resuser.partner_id.id
                respartner       = http.request.env['res.partner'].sudo().search([('id','=',partnerid)])
                db_ciphertext   = resuser.ciphertext ;  db_iv = resuser.iv ; db_key = resuser.key; 
                if(db_ciphertext in (None, False)): db_ciphertext=''
                if(db_iv         in (None, False)): db_iv        =''
                if(db_key        in (None, False)): db_key       =''
                if(  len(resuser)  <(1)):info = 'No user found'   ; dict_tok={'code':410,'message':info}; data_tok.append(dict_tok)
                elif(db_ciphertext ==''):info = 'No ciphertext'   ; dict_tok={'code':411,'message':info}; data_tok.append(dict_tok)
                elif(db_iv         ==''):info = 'No db_iv'        ; dict_tok={'code':413,'message':info}; data_tok.append(dict_tok)
                elif(db_key        ==''):info = 'No db_key'       ; dict_tok={'code':414,'message':info}; data_tok.append(dict_tok)
                else:
                    error = False
                    try:
                        iv          = b64decode(db_iv)           
                        ciphertext  = b64decode(db_ciphertext)   
                        key         = b64decode(db_key)                     
                        cipher      = AES.new(key, AES.MODE_CBC, iv) 
                        plaintext   = unpad(cipher.decrypt(ciphertext), AES.block_size)
                        result=plaintext.decode('utf-8')  
                    except (ValueError, KeyError):
                        error   = True
                        result  = 'ERROR pada saat decrypting stored password'
                        info    = result      ; dict_tok={'Status':'falsed','message':info}; data_tok.append(dict_tok)
                    if(error==False):
                        if(password == result ):
                            info = 'password sesuai'
                            token =  db_ciphertext      
                            
                            data={  'token'     : token,
                                    'name'      : respartner.name,
                                    'email'     : respartner.email,
                                    'mobile'    : respartner.mobile,
                                    'drivertype': respartner.drivertype,
                                    'korlap'    : respartner.korlap.name,
                                    }
                            # dict_tok={  'token'     : token,
                            #             'Status'    :'true',
                            #             'message'   :info}
                            dict_tok={  'code'      : 200,#200=True, else=False
                                        'message'   : info,
                                        'data'    :data,}
                            data_tok.append(dict_tok)
                        else:
                            info ='Wrong Secret Key'
                            dict_tok={'Status':'false','message':info} 
                            dict_tok={  'code'      : 400,#200=True, else=False
                                        'message'   : info, }
                            data_tok.append(dict_tok)
                            
# def ResponseData(code=200, message="success", data=[]):
#         res = {
#             "code": code,
#             "message": message,
#             "data": data
#         }
#         return res
 

        kw=json.dumps(dict_tok) 
        return kw  

    @http.route('/api/get_openorder/', methods=['POST'],type='http',auth='public', csrf=False)
    # @check_valid_secret
    def get_openorder  (self, **kw):   
        token='';   draftwo=''; isSuccess = False; message   = '';  dict_opor ={};data_opor =[]
        mandatory_header = [ 'token',  'userid'];   header_fields = [] ##ini tuh untuk menampun mandatory field yang gak disupport sama user
        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False): header_fields.append(mandatory_field) 
        if len(header_fields) > 0: message = "B2B ODOO MAM missing required data in header %s" %str(header_fields)  
        else:    
            token = kw.get('token')	  ; userid = kw.get('userid')	  
            if(token == ''):message = 'missing token'   
            if(userid== ''):message = 'missing userid'
            else:
                resuser = http.request.env['res.users'].sudo().search([('login','=',userid),('ciphertext','=',token)]) 
                partner_id = resuser.partner_id
                if not resuser.id   : message = 'login not found or token expired '+userid  
                if not partner_id.id: message = 'login found but has no link to res_partner '+userid 
                else: 
                    # draftwo =http.request.env['tl.tr.draftwo'].sudo().search([('driverid','=',partner_id.id),('senddate','!=',False)]) 
                    draftwo =http.request.env['tl.tr.draftwo'].sudo().search([('senddate','!=',False)], limit=2) 
                    if(draftwo ==False): message = 'no data found'
                    else:
                        isSuccess=True
                        for h in draftwo: 
                            dict_opor={     
                            'id'            :h.id,            'dwoid'             :h.dwoid,             'customername'      :h.customerid.name,    'chassisno'         :h.chassisno,  
                            'engineno'      :h.engineno,      'qi_brandcategory'  :h.qi_brandcategory,  'qi_brand'          :h.qi_brand,           'qi_locationfrom'   :h.qi_locationfrom,   
                            'qi_locationto' :h.qi_locationto, 'qi_cost'           :h.qi_cost,           'qi_wayoftransport' :h.qi_wayoftransport,  'triptype'          :h.triptype,   
                            'drivername'    :h.drivername,    'additionalinfo'    :h.additionalinfo,    'qi_trip'           :h.qi_trip,            'qi_jenistransaksi' :h.qi_jenistransaksi, 
                            'donumber'      :h.donumber,      'spe_number'        :h.spe_number,        'qi_jenisunit'      :h.qi_jenisunit,       'wholesalename'     :h.wholesalename.wholesalename,} 
                            for judul in dict_opor:  
                                if(dict_opor.get(judul) in(None, False)): dict_opor.update({judul : ''} )  
                            data_opor.append(dict_opor) 
            hdlist={}
            if(isSuccess): hdlist ={"code":200,"message":"success","data":data_opor,}
            else         : hdlist ={"code":200,"message":"Failed:"+message,"data":'',}
            hddata =[]; hddata.append(hdlist)
        kw=json.dumps(hddata) 
        return kw  