from odoo import http, _, exceptions , api, SUPERUSER_ID, models, fields
import json 
 
 
class apisignin(http.Controller): 
    _secret_key    = 'b03ddf3ca2e714a6548e7495e2a03f5e824eaac9837cd7f159c67b90fb4b7342'
    _client_id     = '54430bcda29ee2ab4d4e41d57476791948ed9144a5ddb2d69a0e9ef3047edcd2' 
    @classmethod
    def get_credentials(cls):
        return {'secret_key': cls._secret_key, 'client_id': cls._client_id}
    
    def checkkw(self, kw):
        resultcode  = 201
        result = True; msg = '' 
        mandatory_header = ['client_id','secret_key','username','password', 'device_id'] 
        header_fields = []  
        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False):
                header_fields.append(mandatory_field)  
        if len(header_fields) > 0: 
            result = False,
            msg    = "(missing required data in header %s" %str(header_fields)  +")"
        if kw.get('secret_key')!=self._secret_key: 
            result = False
            msg    = "(wrong secret_key)" 
        if kw.get('client_id' )!=self._client_id: 
            result = False
            msg    = "(wrong client_id)"  
        return result,resultcode,msg
        
    @http.route('/api/signin/', methods=['POST'],type='http',auth='none', csrf=False)  
    def get_token(self, **kw):   
        ResUsersInstance = http.request.env['res.users'] 
        errormsg = ''  
        result, resultcode,errormsg = self.checkkw(kw) 
        dict={};  
        if (result == False):
            dict={"code": resultcode, "message": "Gagal Login:"+errormsg} 
            kw  =json.dumps(dict) 
            return kw  
        login       = kw.get('username');    password    =kw.get('password')
        clientid    = kw.get('clientid');    secretkey   =kw.get('secretkey')
        device_id   = kw.get('device_id')
        db_name     =http.request.session.db
        loginstate = '';userid=False
        try: 
            http.request.session.authenticate(db_name, login, password)
            userid = http.request.session.uid
            loginstate = 'Succeed'
        except Exception as e:
            loginstate = 'Failed'
             
        if userid:
            session_info        = http.request.env['ir.http'].session_info()    
            user , access_token = ResUsersInstance.check_credentials(userid) 
            ResUsersInstance.updatedeviceid(userid,device_id)    
            datadriver = http.request.env['res.users'].search([('id', '=', userid)])
            dictdriver = {} 
            for record in datadriver:
                logintype = ""
                if (record.partner_id.is_driver):logintype = "Driver"
                if (record.partner_id.is_korlap):logintype = "Korlap"
                 
                dictdriver = {"android_version" : "1.0.23"                                        , "ios_version"   : "1.0.23", 
                              "token"           : self.replacenull(access_token)                  , "name"          : self.replacenull(record.partner_id.name), 
                              "email"           : self.replacenull(record.partner_id.email)       , "mobile"        : self.replacenull(record.partner_id.mobile), 
                              "drivertype"      : self.replacenull(record.partner_id.drivertype)  , "korlap"        : self.replacenull(record.partner_id.korlap.name),
                              "login_type"      : self.replacenull(logintype)                     ,}  
            dict = {"code": 200, "message": "password sesuai", "data": dictdriver}

            kw  =json.dumps(dict) 
            return kw   
        else:  
            dict = {"code": 301, "message": "Gagal Login, User not found or wrong password"}
            kw  =json.dumps(dict) 
        return kw  
    def replacenull(self, data):
        result = data
        if(result==False):
            result = '' 
        return result
        
            