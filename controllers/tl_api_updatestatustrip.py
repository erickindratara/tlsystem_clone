import xmlrpc.client 
from .tl_api_signin import apisignin
from odoo import http, _, exceptions , api, SUPERUSER_ID, models, fields
import json  
 
class apiupdatestatustrip(http.Controller):     
    def checkkw(self, kw):
        resultcode  = 201
        creds           = apisignin.get_credentials()
        gettoken        = kw.get('token')           ; statuslogin    = 'BELUMTAU'
        isdriver        = False                     ; iskorlap       = False
        getlogin        = kw.get('username')        ; getclientid    = kw.get('client_id') 
        getsecretkey    = kw.get('secret_key')      ; woid           = kw.get('woid')     
        latitude        = kw.get('latitude')        
        longitude       = kw.get('longitude')       ; db_name        = http.request.session.db  
        result          = True                      ; msg            = ''            
        header_fields   = []                        ; loginstate     =''                  
        ResUsersInstance= False                     ; userid         = False
        url             = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')  
        mandatory_header= ['client_id'             ,'secret_key'       ,'token'            ,'username'      ,
                            'woid'                  ,'latitude'    ,'longitude']  

        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False): header_fields.append(mandatory_field)  
        if len(header_fields)   >  0                    : result = False; msg    = "(miss header %s" %str(header_fields)+")" ; return result, resultcode,msg
        if getsecretkey         != creds['secret_key']  : result = False; msg    = "(wrong secret_key)"                      ; return result, resultcode,msg
        if getclientid          != creds['client_id']   : result = False; msg    = "(wrong client_id)"                       ; return result, resultcode,msg
        if len(gettoken)        != 40                   : result = False; msg    = "(token is in wrong format)"              ; return result, 301,msg
        ResUsersInstance = http.request.env['res.users'].sudo().search([('customtoken', '=', gettoken),('login', '=', getlogin)])
        if ResUsersInstance.id  == False                : result = False; msg    = "(token: user not found or invalid token)"; return result, 301, msg  
        isdriver    =ResUsersInstance.partner_id.is_driver; iskorlap=ResUsersInstance.partner_id.is_korlap
        tokenowner  = ResUsersInstance.login ; tokenownerid = ResUsersInstance.partner_id.id 
        common      = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) 
        try: 
            userid  = common.authenticate(db_name, tokenowner, gettoken, {})
        except Exception as e:
            result = False; msg    = "(common.userid: failed to authenticate token and user)" +str(e)                       ; return result, resultcode, msg 
        datawo = False
        logininfo = 'Username:'+ str(ResUsersInstance.login)+'Iskorlap:'+str(iskorlap)+'isdriver:'+str(isdriver)
        if(    iskorlap and     isdriver): result= False; msg= "(error. user ini korlap iya, driver iya. belum ada logicnya di sistem.)" ; return result, resultcode, msg 
        if(    iskorlap                 ): result= False; msg= "(error. user ini korlap.)"       ; return result, resultcode, msg 
        if(not iskorlap and not isdriver): result= False; msg= "(error. user ini tidak berhak.)" ; return result, resultcode, msg 
        woid     = kw.get('woid'    ) ; username_driver  = kw.get('username_driver' )
        latitude = kw.get('latitude') ; longitude        = kw.get('longitude'       ) 
        
        real_draftwo    = http.request.env['tl.tr.draftwo'].sudo().search([('dwoid', '=', woid)])
        draftwo_records = http.request.env['tl.tr.draftwo'].sudo().search([('dwoid', '=', woid),#]) di bypass dlu
                                                                            ('stage', 'in',('PLOTREQ'   ,   #100
                                                                                            'PLOTTED'   ,   #200
                                                                                            'MBL/DRVACC',   #400
                                                                                            'MBL/DRVOTW',   #700
                                                                                            'MBL/DRVLCA',   #800
                                                                                            'MBL/DRVIPU',   #810
                                                                                            'MBL/DRVLCB',   #800
                                                                                            'MBL/DRVDNE'))])#900 
        
        listofstatus =  ["PLOTREQ", "PLOTTED", "MBL/DRVACC", "MBL/DRVOTW", "MBL/DRVLCA", "MBL/DRVIPU", "MBL/DRVLCB", "MBL/DRVDNE"]
        max = len(listofstatus)-1 
        currentstage = draftwo_records.stage
        currentindex = listofstatus.index(currentstage)
        nextindex = currentindex+1 
        nextstage = 0 
        if(nextindex > max):   
             msg = 'anda berada di status tertinggi. ['+currentstage+'], tidak bisa update status lg'
             return False, resultcode,msg   
        else: 
            nextstage = listofstatus[nextindex]
          
        if  (len(real_draftwo)==0): 
            result = False ; msg='API/updatestatustrip error: woid[='+woid+'] tidak ditemukan. mohon diperiksa ulang'
        if  (len(draftwo_records)==0): 
            result = False 
            msg='no WO Invalid or stage not in (PLOTREQ[100],PLOTTED[200],MBL/DRVACC[400],MBL/DRVOTW[700],MBL/DRVLCA[800],MBL/DRVIPU[810],MBL/DRVLCB[800],MBL/DRVDNE[900])'
            msg += '[wo yang diluar status tersebut bisa jadi sudah selesai atau masih gantung di transaksi lain.]'
        elif(len(draftwo_records)>1 ): result = False; msg='API/updatestatustrip:API ini hanya untuk update status 1 WO, yang anda ingin lakukan bisa update lebih dari 1 row. error'
        else:  
            for draftwo in draftwo_records: 
                seq=0
                if(len(draftwo.qi_multitrip)==0): result = False; msg='tl_api_plotingwo, qi_multitrip 0'                                     ;return result, resultcode, msg 
                if(len(draftwo.qi_multitrip)==1): result = False; msg='tl_api_plotingwo, qi_multitrip tidak bisa cuma 1'                     ;return result, resultcode, msg
                if(len(draftwo.qi_multitrip)> 2): result = False; msg='tl_api_plotingwo, qi_multitrip tidak bisa lebih dari 2 untuk saat ini';return result, resultcode, msg
                draftwo_records.write({'currentlatitude': latitude, 'currentlongitude': longitude  ,'stage'     : nextstage})
                                    #    'stage'     : 'PLOTTED'
        return result, resultcode,msg 

    @http.route('/api/updateStatusTrip/', methods=['POST'],type='http',auth='none', csrf=False)  
    def getwo(self, **kw):      
        result, resultcode,errormsg  = self.checkkw(kw)   
        dict={} 
        if (result == False): 
            dict={"code": resultcode, "message": "Gagal Update Status:"+errormsg}  
            kw  =json.dumps(dict) 
            return kw  
        else:    
            dict={"code": 200, "message": "Berhasil Update Status"} 
            kw  =json.dumps(dict)  
            return kw  
