import xmlrpc.client
from .tl_api_signin import apisignin 
from odoo import http, _, exceptions , api, SUPERUSER_ID, models, fields
import json  
 
class apicheckversion(http.Controller):     
    def checkkw(self, kw):  
        resultcode  = 201
        creds = apisignin.get_credentials()
        getclientid     = kw.get('client_id'); getsecretkey   =kw.get('secret_key')
        result   = True ; msg  =''  ; header_fields   = []
         
        # mandatory_header = ['client_id','secret_key','token','scanresult', 'woid'] 
        mandatory_header = ['client_id','secret_key'] 
        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False): header_fields.append(mandatory_field)  
        if len(header_fields)   >  0                    : result = False; msg    = "(miss header %s" %str(header_fields)+")" ; return result,resultcode, msg
        if getsecretkey         != creds['secret_key']  : result = False; msg    = "(wrong secret_key)"                      ; return result,resultcode, msg
        if getclientid          != creds['client_id']   : result = False; msg    = "(wrong client_id)"                       ; return result,resultcode, msg
        return result, resultcode,msg 

    @http.route('/api/checkVersion/', methods=['POST'],type='http',auth='none', csrf=False)  
    def checkwo(self, **kw):     
        result,resultcode, errormsg = self.checkkw(kw)   
        dict={} 
        if (result == False):
            dict={"code": resultcode, "message": "Data Tidak Ada:"+errormsg} 
            kw  =json.dumps(dict) 
            return kw  
        else:   
            dict_version = {'android_version':'1.0.23','ios_version':'1.0.23','link_playstore':'https://www.google.com','link_appstore':'https://www.appstore.com',}
            return json.dumps({"code": 200, "message": "success" ,'data':dict_version     })      