import xmlrpc.client
from .tl_api_signin import apisignin 
from odoo import http, _, exceptions , api, SUPERUSER_ID, models, fields
import json  
 
class apicheckwo(http.Controller):     
    def checkkw(self, kw):  
        resultcode  = 201
        creds = apisignin.get_credentials()
        gettoken = kw.get('token') ; getwoid   =kw.get('woid'); getclientid     = kw.get('client_id'); getsecretkey   =kw.get('secret_key'); db_name          = http.request.session.db  
        result   = True            ; msg       =''            ; header_fields   = []                 ; loginstate     =''                  ; ResUsersInstance = False
        userid   = False           ; url       = 'http://127.0.0.1' 
        mandatory_header = ['client_id','secret_key','token','scanresult', 'woid'] 
        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False): header_fields.append(mandatory_field)  
        if len(header_fields)   >  0                    : result = False; msg    = "(miss header %s" %str(header_fields)+")" ; return result,resultcode, msg,False,False
        if getsecretkey         != creds['secret_key']  : result = False; msg    = "(wrong secret_key)"                      ; return result,resultcode, msg,False,False
        if getclientid          != creds['client_id']   : result = False; msg    = "(ass wrong client_id)"                   ; return result,resultcode, msg,False,False
        if len(gettoken)        != 40                   : result = False; msg    = "(token is in wrong format)"              ; return result,301       , msg,False,False
        ResUsersInstance = http.request.env['res.users'].sudo().search([('customtoken', '=', gettoken)])
        if ResUsersInstance.id  == False                : result = False; msg    = "(token: user not found)"                 ; return result,301       , msg,False,False  
        tokenowner  = ResUsersInstance.login  
        url         = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')  
        common      = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) 
        try: 
            userid    = common.authenticate(db_name, tokenowner, gettoken, {})
        except Exception as e:
            result = False; msg    = "(common.userid: failed to authenticate token and user)" +str(e)                        ; return result,resultcode, msg,False,False
        datawo      =  http.request.env['tl.tr.draftwo'].sudo().search([('dwoid', '=', getwoid)])
        if len(datawo)          == 0                    : result = False;msg    = "(wo ("+getwoid+") return 0 row.)"         ; return result,resultcode, msg,False,False  
        return result,resultcode,msg,ResUsersInstance,datawo

    @http.route('/api/checkWO/', methods=['POST'],type='http',auth='none', csrf=False)  
    def checkwo(self, **kw):     
        result, resultcode, errormsg, ResUsersInstance  , datawo= self.checkkw(kw)   
        dict={} 
        if (result == False):
            dict={"code": resultcode, "message": "Transaction Halted:"+errormsg} 
            kw  =json.dumps(dict) 
            return kw  
        else: 
            scanresult  = kw.get('scanresult') 
            datasesuai = False
            for record in datawo:   
                if scanresult in ['record.chassisno, record.engineno']:
                # if scanresult in ['8998989100120']: 
                    datasesuai = True 
            if (datasesuai) : return json.dumps({"code": 200, "message": "data sesuai"      })    
            else            : return json.dumps({"code": 201, "message": "data tidak sesuai"})     
