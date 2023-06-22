import xmlrpc.client 
from .tl_api_signin import apisignin
from odoo import http, _, exceptions , api, SUPERUSER_ID, models, fields
import json  
 
class apiplotingwo(http.Controller):     
    def checkkw(self, kw):
        resultcode  = 201
        creds       = apisignin.get_credentials()
        gettoken    = kw.get('token') ; statuslogin = 'BELUMTAU'; isdriver=False; iskorlap=False
        getlogin    = kw.get('username')  
        getclientid = kw.get('client_id'); getsecretkey   =kw.get('secret_key'); 
        woid                = kw.get('woid')                ; username_driver       = kw.get('username_driver')
        latitude_asal       = kw.get('latitude_asal')       ; longitude_asal        = kw.get('longitude_asal')
        alamat_lengkap_asal = kw.get('alamat_lengkap_asal') ; latitude_tujuan       = kw.get('latitude_tujuan')
        longitude_tujuan    = kw.get('longitude_tujuan')     ; alamat_lengkap_tujuan = kw.get('alamat_lengkap_tujuan')


        db_name     = http.request.session.db  
        result   = True            ; msg       =''            ; header_fields   = []                 ; loginstate     =''                  ; ResUsersInstance = False
        userid   = False           ; url       =http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')  
        mandatory_header = ['client_id'             ,'secret_key'       ,'token'            ,'username'      ,
                            'woid'                  ,'username_driver'  ,'latitude_asal'    ,'longitude_asal',
                            'alamat_lengkap_asal'   ,'latitude_tujuan'  ,'longitude_tujuan' ,'alamat_lengkap_tujuan'
                            ]  

        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False): header_fields.append(mandatory_field)  
        if len(header_fields)   >  0                    : result = False; msg    = "(miss header %s" %str(header_fields)+")" ;                  return result, resultcode,msg
        if getsecretkey         != creds['secret_key']  : result = False; msg    = "(wrong secret_key)"                      ;                  return result, resultcode,msg
        if getclientid          != creds['client_id']   : result = False; msg    = "(wrong client_id)"                       ;                  return result, resultcode,msg
        if len(gettoken)        != 40                   : result = False; msg    = "(token is in wrong format)"              ; resultcode=301;  return result, resultcode,msg
        ResUsersInstance = http.request.env['res.users'].sudo().search([('customtoken', '=', gettoken),('login', '=', getlogin)])
        if ResUsersInstance.id  == False                : result = False; msg    = "(token: user not found or invalid token)"; resultcode=301;  return result, resultcode,msg  
        isdriver=ResUsersInstance.partner_id.is_driver; iskorlap=ResUsersInstance.partner_id.is_korlap
        tokenowner  = ResUsersInstance.login ; tokenownerid = ResUsersInstance.partner_id.id 
        common      = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) 
        try: 
            userid  = common.authenticate(db_name, tokenowner, gettoken, {})
        except Exception as e:
            result = False; msg    = "(common.userid: failed to authenticate token and user)" +str(e)                    ; return result, resultcode,msg 
        datawo = False
        logininfo = 'Username:'+ str(ResUsersInstance.login)+'Iskorlap:'+str(iskorlap)+'isdriver:'+str(isdriver)
        if(iskorlap and isdriver)   : result      = False; msg    = "(error. user ini korlap iya, driver iya. belum ada logicnya di sistem.)" ; return result, resultcode,msg 
        if(             isdriver)   : result      = False; msg    = "(error. user ini driver.)" ; return result, resultcode,msg 
         
        draftwo_records = http.request.env['tl.tr.draftwo'].sudo().search([('dwoid', '=', woid),('stage', 'in', ('PLOTTED','PLOTREQ') )])
        woid                = kw.get('woid')                ; username_driver       = kw.get('username_driver')
        latitude_asal       = kw.get('latitude_asal')       ; longitude_asal        = kw.get('longitude_asal')
        alamat_lengkap_asal = kw.get('alamat_lengkap_asal') ; latitude_tujuan       = kw.get('latitude_tujuan')
        longitude_tujuan    = kw.get('longitude_tujuan')    ; alamat_lengkap_tujuan = kw.get('alamat_lengkap_tujuan')
        datadriver          = http.request.env['res.users'].sudo().search([('login', '=', username_driver),('partner_id.is_driver','=',True  )])

        if  (len(datadriver     )==0): result = False; msg='driver username invalid, or not found)'
        elif(len(draftwo_records)==0): result = False; msg='no WO Invalid or stage not in (PLOTTED[200],PLOTREQ[100])'
        elif(len(draftwo_records)>1 ): result = False; msg='API ini hanya show 1 row, ini show 2 row. error'
        else:  
            for draftwo in draftwo_records: 
                seq=0
                if(len(draftwo.qi_multitrip)==0): result = False; msg='tl_api_plotingwo, qi_multitrip 0'                                     ;return result, resultcode,msg 
                if(len(draftwo.qi_multitrip)==1): result = False; msg='tl_api_plotingwo, qi_multitrip tidak bisa cuma 1'                     ;return result, resultcode,msg
                if(len(draftwo.qi_multitrip)> 2): result = False; msg='tl_api_plotingwo, qi_multitrip tidak bisa lebih dari 2 untuk saat ini';return result, resultcode,msg
                for draftwoitem in draftwo.qi_multitrip.sorted('dwo_sequence'):
                    seq +=1 
                    if(seq==1):draftwoitem.write({ 'dwo_latitude'  :latitude_asal   , 'dwo_longitude' :longitude_asal   ,'dwo_alamat':alamat_lengkap_asal  })  
                    if(seq> 1):draftwoitem.write({ 'dwo_latitude'  :latitude_tujuan , 'dwo_longitude' :longitude_tujuan ,'dwo_alamat':alamat_lengkap_tujuan})  
                quotseq = 0
                dataquotationmultitrip = http.request.env['tl.tr.quotationitem.multitrip'].sudo().search([('quotationitemid', '=', draftwo.quotationitemID)])
                for item in dataquotationmultitrip.sorted('sequence'): 
                    quotseq+=1 
                    if(quotseq==1):item.write({ 'locationfromlatitude'  :latitude_asal   , 'locationfromlongitude' :longitude_asal   ,'locationfromalamat':alamat_lengkap_asal  })  
                    if(quotseq> 1):item.write({ 'locationfromlatitude'  :latitude_tujuan , 'locationfromlongitude' :longitude_tujuan ,'locationfromalamat':alamat_lengkap_tujuan})       
                draftwo_records.write({'driverid'       : datadriver.partner_id.id          , 'drivername': datadriver.partner_id.name  , 
                                       'rp_phone'       : datadriver.partner_id.phone       , 'rp_mobile' : datadriver.partner_id.mobile,
                                       'rp_drivertype'  : datadriver.partner_id.drivertype  , 'stage'     : 'PLOTTED'})
        return result, resultcode,msg 

    @http.route('/api/plotingWO/', methods=['POST'],type='http',auth='none', csrf=False)  
    def getwo(self, **kw):      
        result, resultcode, errormsg  = self.checkkw(kw)   
        dict={} 
        if (result == False): 
            dict={"code": resultcode, "message": "Gagal Ploting:"+errormsg}  
            kw  =json.dumps(dict) 
            return kw  
        else:    
            dict={"code": 200, "message": "Berhasil Ploting WO"} 
            kw  =json.dumps(dict)  
            return kw  
            