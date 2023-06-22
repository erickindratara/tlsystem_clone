# import xmlrpc.client 
# from .tl_api_signin import apisignin
# from odoo import http, _, exceptions , api, SUPERUSER_ID, models, fields
# import json  
 
# class apigetlistdriverbykorlap(http.Controller):     
#     def checkkw(self, kw):
#         creds       = apisignin.get_credentials()
#         gettoken    = kw.get('token') ; statuslogin = 'BELUMTAU'; isdriver=False; iskorlap=False
#         getlogin    = kw.get('username')  
#         getclientid = kw.get('client_id'); getsecretkey   =kw.get('secret_key'); 
#         db_name     = http.request.session.db  
#         result   = True            ; msg       =''            ; header_fields   = []                 ; loginstate     =''                  ; ResUsersInstance = False
#         userid   = False           ; url       =http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')  
#         mandatory_header = ['client_id','secret_key','token','username']  
#         for mandatory_field in mandatory_header: 
#             if not kw.get(mandatory_field,False): header_fields.append(mandatory_field)  
#         if len(header_fields)   >  0                    : result = False; msg    = "(miss header %s" %str(header_fields)+")" ; return result, msg,False,False
#         if getsecretkey         != creds['secret_key']  : result = False; msg    = "(wrong secret_key)"                      ; return result, msg,False,False
#         if getclientid          != creds['client_id']   : result = False; msg    = "(wrong client_id)"                       ; return result, msg,False,False
#         if len(gettoken)        != 40                   : result = False; msg    = "(token is in wrong format)"              ; return result, msg,False,False
#         ResUsersInstance = http.request.env['res.users'].sudo().search([('customtoken', '=', gettoken),('login', '=', getlogin)])
#         if ResUsersInstance.id  == False                : result = False; msg    = "(token: user not found or invalid token)"; return result, msg,False,False  
#         isdriver=ResUsersInstance.partner_id.is_driver; iskorlap=ResUsersInstance.partner_id.is_korlap
#         tokenowner  = ResUsersInstance.login ; tokenownerid = ResUsersInstance.partner_id.id 
#         common      = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) 
#         try: 
#             userid  = common.authenticate(db_name, tokenowner, gettoken, {})
#         except Exception as e:
#             result = False; msg    = "(common.userid: failed to authenticate token and user)" +str(e)                    ; return result, msg,False,False
#         datadriver = False
#         logininfo = 'Username:'+ str(ResUsersInstance.login)+'Iskorlap:'+str(iskorlap)+'isdriver:'+str(isdriver)
#         datadriver = http.request.env['tl.tr.draftwo'].sudo().search([('stage', '=', 'PLOTREQ'),('korlap_id', '=', tokenownerid)]) 
#         if(iskorlap==True)   : result      = False; msg    = "(error. user ini korlap iya, driver iya. belum ada logicnya di sistem.)" ; return result, msg,False,False
#         if(iskorlap==False)   : result      = False; msg    = "(error. user ini korlap iya, driver iya. belum ada logicnya di sistem.)" ; return result, msg,False,False
#         if len(datadriver) == 0         : result      = False; msg    = "logininfo:"+logininfo+"(getwo return "+str(len(datadriver))+" row.)"                                                   ; return result, msg,False,False
#         return result, msg,ResUsersInstance,datadriver
#         # return result, msg,datawo

#     @http.route('/api/getListDriverByKorlap/', methods=['POST'],type='http',auth='none', csrf=False)  
#     def getgetListDriverByKorlap(self, **kw):      
#         result, errormsg  , ResUsersInstance, datawo= self.checkkw(kw)   
#         dict={}; data =[]
#         if (result == False):
#             dict={"code": 301, "message": "Transaction Halted:"+errormsg}
#             data.append(dict)
#             kw  =json.dumps(data) 
#             return kw  
#         else:   
#             for record in datawo:      
#                 shortorder = record.qi_jenistransaksi
#                 tipe_order = {"DU": "Delivery Unit", "LOG": "Logistic"}.get(shortorder, "unknown order type")
#                 dt_senddate        = record.senddate  
#                 tanggal_estimasi="";jam_estimasi=""
#                 if(dt_senddate==False): 
#                     tanggal_estimasi="";jam_estimasi=""
#                 else:
#                     tanggal_estimasi= dt_senddate.strftime("%d-%m-%Y")      
#                     jam_estimasi    = dt_senddate.strftime("%H:%M") 
                
#                 dt_delivereddate = record.delivereddate 
#                 tanggal_estimasiselesai="";jam_estimasiselesai=""
#                 if(dt_delivereddate==False): tanggal_estimasiselesai="";jam_estimasiselesai=""
#                 else:
#                     tanggal_estimasiselesai= dt_delivereddate.strftime("%d-%m-%Y")      
#                     jam_estimasiselesai    = dt_delivereddate.strftime("%H:%M") 
#                 korlap           = record.korlap_id.name     or ""      ;driver         = record.driverid.name or ""
#                 wot              = record.qi_wayoftransport  or ""      ;nopolcarrier   = record.licenseplate or ""
#                 qi_locationfrom  = record.qi_locationfrom    or ""      
#                 if not driver: driver = ""
#                 data_multitrip = []
#                 data_itemlogistic = []
#                 dict_itemlogistic = {'nama_barang':'Sepatu Kulit'}
#                 data_itemlogistic.append(dict_itemlogistic)
#                 if(shortorder=='DU'): data_itemlogistic = []
#                 dwo_sequence =0
#                 for record_dt  in sorted(record.qi_multitrip, key=lambda r: r.dwo_sequence):
#                     dwo_sequence +=1
#                     dict_multitrip = {
#                             'sequence'              :dwo_sequence ,
#                             'lokasi_tujuan'         :record_dt.dwo_locationfrom ,
#                             'latitude'              :'0'            ,'longitude'         :'0',
#                             'tanggal_estimasitiba'  :'12-02-2023'   ,'jam_estimasitiba'  :'16:00',
#                             'tanggal_aktualtiba'    :'12-02-2023'   ,'jam_aktualtiba'    :'19:00',
#                             'itemlogistic'          :data_itemlogistic}  
#                     data_multitrip.append(dict_multitrip)
#                 dict_itemcar = {}; data_itemcar = []
#                 dict_itemcar = {'engine_no'   :record.engineno ,'chassis_no' :record.chassisno   ,
#                                 'vehicle_name':record.qi_brand ,'no_polisi'  :record.licenseplate,}  
#                 data_itemcar.append(dict_itemcar)
#                 if(shortorder=='LOG'): data_itemcar = []
#                 data_draftwo = []
#                 dict_draftwo ={ 
#                                 'no_wo'                     :record.dwoid            ,
#                                 'status_code'               : 100                    ,
#                                 'status_order'              :"Need Driver Allocation",
#                                 'bg_color_status_order'     :"ad3802"                ,
#                                 'text_color_status_order'   :"ededed"                ,
#                                 'tipe_order'                :tipe_order              ,
#                                 'tanggal_estimasipickup'    :tanggal_estimasi        ,
#                                 'jam_estimasipickup'        :jam_estimasi            , 
#                                 'korlap'                    :korlap                  ,
#                                 'driver_name'               :driver                  ,
#                                 'way_of_transport'          :wot                     ,
#                                 'nopol_carrier'             :nopolcarrier            , 
#                                 'itemcar'                   :data_itemcar            ,  
#                                 'lokasi_jemput'             : qi_locationfrom        ,
#                                 'latitude'                  : "0"                    ,
#                                 'longitude'                 : "0"                    ,
#                                 'tanggal_estimasiselesai'   :tanggal_estimasiselesai ,
#                                 'jam_estimasiselesai'       :jam_estimasiselesai     ,
#                                 'tanggal_aktualselesai'     :""                      ,
#                                 'jam_aktualselesai'         :""                      ,
#                                 'trip'                      :data_multitrip          
#                                 } 
#                 data_draftwo.append(dict_draftwo)
            
            
#             dict={"code": 200, "message": "success","data":data_draftwo} 
#             kw  =json.dumps(dict)  
#             return kw  
            