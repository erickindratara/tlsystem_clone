import xmlrpc.client 
from .tl_api_signin import apisignin
from odoo import http, _, exceptions , api, SUPERUSER_ID, models, fields
import json  
 
class apigetwobyID(http.Controller):     
    def checkkw(self, kw):
        resultcode  = 201
        creds       = apisignin.get_credentials()
        gettoken    = kw.get('token') ; statuslogin = 'BELUMTAU'; isdriver=False; iskorlap=False
        getlogin    = kw.get('username')  
        getclientid = kw.get('client_id'); getsecretkey   =kw.get('secret_key'); 
        getwoid     = kw.get('woid').strip() 
        db_name     = http.request.session.db  
        result   = True            ; msg       =''            ; header_fields   = []                 ; loginstate     =''                  ; ResUsersInstance = False
        userid   = False           ; url       =http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')  
        mandatory_header = ['client_id','secret_key','token','username','woid']  

        for mandatory_field in mandatory_header: 
            if not kw.get(mandatory_field,False): header_fields.append(mandatory_field)  
        if len(header_fields)   >  0                    : result = False; msg    = "(miss header %s" %str(header_fields)+")" ; return result,resultcode, msg,False,False,False
        if getsecretkey         != creds['secret_key']  : result = False; msg    = "(wrong secret_key)"                      ; return result,resultcode, msg,False,False,False
        if getclientid          != creds['client_id']   : result = False; msg    = "(wrong client_id)"                       ; return result,resultcode, msg,False,False,False
        if len(gettoken)        != 40                   : result = False; msg    = "(token is in wrong format)"              ; return result,301       , msg,False,False,False
        ResUsersInstance = http.request.env['res.users'].sudo().search([('customtoken', '=', gettoken),('login', '=', getlogin)])
        print('kambing0',ResUsersInstance)
        print('kambing0x',ResUsersInstance.id)
        if ResUsersInstance.id  == False                : result = False; msg    = "(token: user not found or invalid token)"; return result,301       , msg,False,False,False
        isdriver    = ResUsersInstance.partner_id.is_driver; iskorlap=ResUsersInstance.partner_id.is_korlap
        
        tokenowner  = ResUsersInstance.login ; tokenownerid = ResUsersInstance.partner_id.id 
        common      = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) 
        try: 
            userid  = common.authenticate(db_name, tokenowner, gettoken, {})
        except Exception as e:
            result = False; msg    = "(common.userid: failed to authenticate token and user)" +str(e)                    ; return result,resultcode, msg,False,False,False

        datawo      = False; datadriver = False
        logininfo   = 'Username:'+ str(ResUsersInstance.login)+'Iskorlap:'+str(iskorlap)+'isdriver:'+str(isdriver) 
        # datawo      = http.request.env['tl.tr.draftwo'].sudo().search([])
        datawo      = http.request.env['tl.tr.draftwo'].sudo().search(['&',('dwoid', '=', getwoid),
                      ('stage', 'in', ('PLOTREQ'   ,'PLOTTED'   ,'MBL/DRVACC','MBL/DRVOTW','MBL/DRVLCA','MBL/DRVIPU','MBL/DRVLCB','MBL/DRVDNE')),])
        why0        = http.request.env['tl.tr.draftwo'].sudo().search([('dwoid', '=', getwoid),])
        if(iskorlap and isdriver)   : result      = False; msg    = "(error. user ini korlap iya, driver iya. belum ada logicnya di sistem.)" ; return result,resultcode, msg,False,False,False
        if len(datawo) == 0         : 
            result      = False;msg    = "logininfo:"+logininfo+"(getwobyID return "+str(len(datawo))+" row.)"         
            if(why0.stage): msg = "sebenarnya ada, tapi stage diluar range. Stage["+why0.stage+'] stage yang dicari:[(PLOTREQ),(PLOTTED),(MBL/DRVACC),(MBL/DRVOTW),(MBL/DRVLCA),(MBL/DRVIPU),(MBL/DRVLCB),(MBL/DRVDNE)]'
        datadriver      = http.request.env['res.users'].sudo().search([('partner_id.is_driver', '=', True)])
        return result,resultcode, msg,ResUsersInstance,datawo, datadriver
        
    @http.route('/api/getWOById/', methods=['POST'],type='http',auth='none', csrf=False)  
    def getwo(self, **kw):       
        result, resultcode,errormsg  , ResUsersInstance, datawo, datadriver = self.checkkw(kw)     

        dict={} 
        if (result == False):
            dict={"code": resultcode, "message": "Data Tidak Ada:"+errormsg} 
            kw  =json.dumps(dict) 
            return kw  
        else:   
            if(ResUsersInstance.partner_id.is_korlap): typeuser='Korlap'
            if(ResUsersInstance.partner_id.is_driver): typeuser='Driver'  
            data_driver = []
            for rec in datadriver: 
                dict_driver = {'username'   :rec.login , 'driver_name' :rec.name , }  
                data_driver.append(dict_driver)
            for record in datawo:   
                shortorder = record.qi_jenistransaksi   
                tipe_order = {"DU": "Delivery Unit", "LOG": "Logistic"}.get(shortorder, "unknown order type")
                stage = record.stage
                stagedesc = 'Unknown ['+stage+']'
                stagecode = '000'
                notes = record.salesdescription if record.salesdescription else ''
                actbtn    = 'button invalid stage['+stage+']' ;bg_color_status_order=''
                if(stage =='PLOTREQ'    ): stagedesc=           "Need Driver Allocation" ; stagecode=100; bg_color_status_order='004da6'
                if(stage =='PLOTTED'    ): stagedesc=          "Driver has been plotted" ; stagecode=200; bg_color_status_order='004da6'; actbtn = 'Terima Order'
                if(stage =='MBL/DRVACC' ): stagedesc=            "Driver Accepted Order" ; stagecode=400; bg_color_status_order='57a800'; actbtn = 'On The Way'
                if(stage =='MBL/DRVOTW' ): stagedesc=   "Driver is On the way(to Loc A)" ; stagecode=700; bg_color_status_order='47423b'; actbtn = 'On Location'
                if(stage =='MBL/DRVLCA' ): stagedesc=             "Driver on Location A" ; stagecode=800; bg_color_status_order='690050'; actbtn = 'Pickup Barang'
                if(stage =='MBL/DRVIPU' ): stagedesc=                   "Item Picked Up" ; stagecode=810; bg_color_status_order='033f45'; actbtn = 'Drop Barang'
                if(stage =='MBL/DRVLCB' ): stagedesc=       "Item Dropped on Location B" ; stagecode=800; bg_color_status_order='381e04'; actbtn = 'End Order'
                if(stage =='MBL/DRVDNE' ): stagedesc=                       "Order Done" ; stagecode=900; bg_color_status_order='7a0000'

                dt_senddate        = record.senddate  
                tanggal_estimasi="";jam_estimasi=""
                if(dt_senddate==False): 
                    tanggal_estimasi="";jam_estimasi=""
                else:
                    tanggal_estimasi= dt_senddate.strftime("%d-%m-%Y")      
                    jam_estimasi    = dt_senddate.strftime("%H:%M")  
                korlap           = record.korlap_id.name     or ""      ;driver         = record.driverid.name  or ""
                wot              = record.qi_wayoftransport  or ""      ;nopolcarrier   = record.licenseplate   or "" 
                if not driver: driver = ""
                data_multitrip  = []
                dwo_sequence    = 0
                for record_dt  in sorted(record.qi_multitrip, key=lambda r: r.dwo_sequence):
                    dwo_sequence +=1 
                    data_itemlogistic = []
                    dict_itemlogistic = {}
                    if(record.qi_jenistransaksi == 'LOG'):
                        load = record_dt.dwo_item_load; unload = record_dt.dwo_item_load
                        if(load!=False and load !='n/a'):
                            load = 'load: '+load
                        else: load = ''
                        if(unload!=False and unload !='n/a'):
                            unload = 'unload: '+unload
                        else: unload = ''
                        nama_barang = load+unload
                        dict_itemlogistic = {'nama_barang':nama_barang}
                        data_itemlogistic.append(dict_itemlogistic)
                    senddateest = record.senddate.strftime("%d-%m-%Y")           if record.senddate             else ''
                    sendtimeest = record.senddate.strftime("%H:%M")              if record.senddate             else ''
                    dlvdateest = record.delivereddate.strftime("%d-%m-%Y")       if record.delivereddate        else ''
                    dlvtimeest = record.delivereddate.strftime("%H:%M")          if record.delivereddate        else ''
                    loc_tuju    = record_dt.dwo_locationfrom                     if record_dt.dwo_locationfrom  else ''
                    ala_tuju    = record_dt.dwo_alamat                           if record_dt.dwo_alamat        else ''
                    lat         = record_dt.dwo_latitude                         if record_dt.dwo_latitude      else '' 
                    long        = record_dt.dwo_longitude                        if record_dt.dwo_latitude      else '' 
                    long        = record_dt.dwo_longitude                        if record_dt.dwo_longitude     else ''
                    senddateact = record.senddateactual.strftime("%d-%m-%Y")     if record.senddateactual       else ''
                    sendtimeact = record.senddateactual.strftime("%H:%M")        if record.senddateactual       else ''  
                    dlvdateact  = record.delivereddateactual.strftime("%d-%m-%Y")if record.delivereddateactual  else '' 
                    dlvtimeact  = record.delivereddateactual.strftime("%H:%M")   if record.delivereddateactual  else '' 
                    if(shortorder=='DU'): data_itemlogistic = []  
                    dict_multitrip = {
                            'sequence'              :dwo_sequence ,
                            'lokasi_tujuan'         :loc_tuju,
                            'alamat_tujuan'         :ala_tuju,
                            'latitude'              :lat,
                            'longitude'             :long,
                            'tanggal_estimasitiba'  :dlvdateest,
                            'jam_estimasitiba'      :dlvtimeest, 
                            'tanggal_aktualtiba'    :dlvdateact   ,
                            'jam_aktualtiba'        :dlvtimeact,
                            'itemlogistic'          :data_itemlogistic}  
                    data_multitrip.append(dict_multitrip)
                dict_itemcar = {}; data_itemcar = [] 
                dict_itemcar = {'engine_no'   :record.engineno      if record.engineno      else '',
                                'chassis_no'  :record.chassisno     if record.chassisno     else '',
                                'vehicle_name':record.qi_brand      if record.qi_brand      else '',
                                'no_polisi'   :record.licenseplate  if record.licenseplate  else ''}  
                data_itemcar.append(dict_itemcar)
                if(shortorder=='LOG'): data_itemcar = []
                data_draftwo = []
                enable_barcode = 0
                if(record.custinitial =='TMP'):
                    enable_barcode = 1
                dict_draftwo ={ 
                                'no_wo'                     :record.dwoid            ,
                                'status_code'               :stagecode               ,#ini
                                "status_order"              :stagedesc               ,#ini
                                "action_button"             :actbtn                  ,#ini
                                "type"                      :typeuser                ,#ini
                                'bg_color_status_order'     :bg_color_status_order   ,
                                'text_color_status_order'   :"EDEDED"                ,
                                'tipe_order'                :tipe_order              ,
                                'tanggal_estimasipickup'    :tanggal_estimasi        , 
                                'jam_estimasipickup'        :jam_estimasi            , 
                                'korlap'                    :korlap                  ,
                                'driver_name'               :driver                  ,
                                'way_of_transport'          :wot                     ,
                                'carrier_name'              :record.carrier_name.carriername  if record.carrier_name.carriername   else '',
                                'nopol_carrier'             :record.carrier_nopol if record.carrier_nopol  else '' ,
                                'itemcar'                   :data_itemcar            ,  
                                'notes'                     :notes                   ,
                                'trip'                      :data_multitrip          ,
                                'listdriver'                :data_driver,
                                'enable_set_pickup_loc'     :0,
                                'enable_set_destination_loc':0,
                                'enable_scan_barcode'       :enable_barcode,                      
                                } 
                data_draftwo.append(dict_draftwo)
            
            
            dict={"code": 200, "message": "success","data":data_draftwo} 
            kw  =json.dumps(dict)  
            return kw  
            