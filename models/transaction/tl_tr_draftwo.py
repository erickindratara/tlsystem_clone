from ast import Store
from cgitb import text
from ctypes import create_unicode_buffer
from dataclasses import replace
from email.policy import default
from http.client import FOUND
from operator import truediv
from tracemalloc import DomainFilter
from typing_extensions import Required
from venv import create
from weakref import ref
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta 
try:
    import simplejson as json
except ImportError:
    import json
 
class IrFilters(models.Model):
    _inherit = 'ir.filters'  
     
class dwoadditionalinfo(models.Model): #
    _name           = 'tl.ms.dwoadditionalinfo' #nama di db berubah jadi training_course
    _description    = 'Master WO Additional Info' 
    _rec_name       = 'additionalinfo'  
    additionalinfo  = fields.Char(string=  'Additional info (input SS customer name)')

class dwocarrierinfo(models.Model): #
    _name           = 'tl.ms.dwocarrierinfo' #nama di db berubah jadi training_course
    _description    = 'Master WO carrier Info' 
    _rec_name       = 'carriername'   
    def name_get(self):
        result = []  
        for s in self:  
            name ='' 
            fdt=False
            a = str(s.carriername)
            b = str(s.carriernopol)
            if(a in(None, False)): a= '[--]'
            if(b in(None, False)): b= '[--]'    
            name = a+'  Nopol: '+b
            result.append((s.id,name))  
        return result 

    carriername     = fields.Char(string=  'Carrier Name')
    carriernopol    = fields.Char(string=  'Carrier Nopol')
class dwobrandinfo(models.Model): #
    _name           = 'tl.ms.dwobrandinfo' #nama di db berubah jadi training_course
    _description    = 'Master WO brand Info' 
    _rec_name       = 'brandname'   
    # manufacturer  =fields.Many2one('tl.ms.productbrand', string="manufacturer", Required=True)  sementara di open all
    manufacturer  =fields.Many2one('tl.ms.productbrand', string="manufacturer")    
    brandname     = fields.Char(string=  'brand Name')

class draftwo(models.Model): #
    _name           = 'tl.tr.draftwo' #nama di db berubah jadi training_course
    _description    = 'Transaction WO'  
    _rec_name       = 'dwoid'  

    def cekdefaultfilter(self):  
        ir_filters = self.env['ir.filters'].sudo(); ir_filters.search([('model_id', '=', 'tl.tr.draftwo')]).sudo().unlink()  
        ir_filters.sudo().create({ 
            'model_id'  : 'tl.tr.draftwo' ,'name'      : "stage in New, Draft. Group by Send Date"   ,
            'active'    : 'True'          ,'domain'    : '[]'  ,
            # 'active'    : 'True'          ,'domain'    : '[["stage","in",("NEW","DRF")]]'  ,
            # 'sort'      : "[]"            ,'context'   : "{'group_by': ['customerid','senddate:week']}",
            'sort'      : "[]"            ,'context'   : "{'group_by': ['customerid','activestage','stage']}",
            'is_default': 'True',})
                 

    filterquotationbywayoftransport = fields.Selection([('SELFDRIVE', 'Self Drive'),('TRUCKING', 'Trucking'),('TOWING', 'Towing'),('CARRIER', 'Car Carrier')], string='Filter', default='SELFDRIVE')
     
    @api.onchange('filterquotationbywayoftransport')
    def fqbwot_onchange(self):   
        the_domain = self.quotationdomain()
        return the_domain
 
    def quotationdomain(self): 
        self.qi_multitrip =False
        cust_domain     = [('customerid', '=', self.customerid.id)] ; overalldomain   = False
        fqbwot          = self.filterquotationbywayoftransport      ; jenistransaksi  ="BO"
        wot_domain      =  [('wayoftransport', '=', fqbwot)] 
        if(self.drafttype=="DESTINATION"    ): jenistransaksi = "DU"
        if(self.drafttype=="DESTINATIONLOG" ): jenistransaksi = "LOG"
        jenistrans_domain = [('jenistransaksi', '=', jenistransaksi)]
        if(self.customerid.id)  : 
            if(overalldomain): overalldomain += cust_domain 
            else             : overalldomain = cust_domain
        if(self.drafttype)   : 
            if(overalldomain): overalldomain += jenistrans_domain 
            else             : overalldomain = jenistrans_domain 
        if(fqbwot)           :  
            if(overalldomain): overalldomain += wot_domain 
            else             : overalldomain = wot_domain 
        the_domain = False
        if(overalldomain):
            the_domain = {'domain': {'quotationitem':overalldomain }} 
        self.quotationitem = False
        return  the_domain
          

    #coding customer id start 
   
    PJAllocationNotes           =fields.Char(string='Catatan Alokasi', default='Ongkos dan Jasa Driver' )  
    quotationitem               =fields.Many2one('tl.tr.quotationitem', string="Quotation Item ID", Required=True)  
    @api.onchange('customerid')
    def cus_onchange(self):  
        if(self.customerid not in(None,False)): 
            self.custinitial    = self.customerid.companyinitial 
            tblcustomer         = self.env['res.partner'].search([('id', '=', self.customerid.id)], limit=1)    
            if(tblcustomer.name  in('PT Surya Sudeco','PT Tunas Mobilindo perkasa')):         self.drafttype ="DESTINATION" 
            else:   self.drafttype ="DESTINATIONLOG" 
            self._cr.execute( """ update tl_ms_user set defaultcustomer =  '"""+str(self.customerid.id)+"""'  where user_id = '"""+str(self.env.user.id)+"""' """) 
        if(self.dwoid_temporary in (False, None)): self.dwoid_temporary = self.default_temp()   
        the_domain = self.quotationdomain()
        return the_domain
 
    def newdefault(self):     
        return self.getdefaultcustomerid()   
 
     
    customerid = fields.Many2one('res.partner', string='Customer Name' , required=True, default=newdefault,   domain=[('is_logistic_customer','=',1)])   
 
    # korlapid                    =fields.Char     (string='Korlap'       ,default='')    
    korlap_id = fields.Many2one('res.partner', string='Korlap' , required=True,   domain=[('is_korlap','=',1),])   
 
    def getdefaultcustomerid(self): 
        str_a = 'x' 
        try:
            str_a = str(self.env.user.id)
        except ValueError:
            str_a = str(1) 
        get_employee = """ SELECT    distinct   b.defaultcustomer FROM   res_users a inner join tl_ms_user b on a.id = b.user_id   where a.id = '"""+str(str_a)+"""' """
        self._cr.execute(get_employee)  
        var_a = self._cr.dictfetchone()     
        maxloop = 10 
        while(var_a == None and maxloop >0):
            maxloop=maxloop-1 
            insert =  """ insert into tl_ms_user (user_id, defaultcustomer) values ("""+str_a+""",(select   id from res_partner where is_company =True order by is_logistic_customer asc limit 1)) """
            self._cr.execute(insert)   
            self._cr.execute(get_employee)   
            var_a = self._cr.dictfetchone()    

        defaultcustomer =var_a.get('defaultcustomer')   
        return int(defaultcustomer)
 
    @api.model
    def _getcorrectcust(self):    
        defaultcus  = self.env['tl.ms.user'].search([('user_id', '=', self.env.user.id)], limit=1)    
        for record in self: 
            defcus = defaultcus.defaultcustomer.id 
            str_a = str(record['customerid'].id)  
            if str(defcus) == str_a : 
                record['iscorrectcust'] = True
            else:
                record['iscorrectcust'] = False

              
    def _value_search(self, operator, value):
        field_id = self.search([]).filtered(lambda x : x.iscorrectcust == value )
        return [('id', operator, [x.id for x in field_id] if field_id else False )]
      
    iscorrectcust = fields.Boolean(compute='_getcorrectcust',string="iscorrectcust", store=False,search='_value_search')

    custinitial = fields.Char(string='Customer Initial' ) 
    # custeditable = fields.Boolean(string='Customer editable') 
    dwoid_temporary = fields.Char(string='dwoid_temporary' )    
    #coding customer id end  
 
    def datesend(self): 
        current_date = fields.datetime.now()  
        return current_date + timedelta(days=7) 

    def datetoday(self): 
        return fields.datetime.now()

    def getcustinitial(self): 
        custinit = '' 
        x  = self.env['tl.ms.user'].search([('user_id', '=', self.env.user.id)], limit=1)
        custinit  = x.defaultcustomer.companyinitial 
        return custinit 


    PJAllocationNotes           =fields.Char(string='Catatan Alokasi', default='Ongkos dan Jasa Driver' )       
    isupload                    =fields.Boolean(string="isupload", default=False) 
    isforminput                 =fields.Boolean(string="isforminput", default=True) 
    #jika upload
    quotationitem_get           =fields.Integer(string ='quotationitem_get')   
    #jika upload
    driverid                    =fields.Many2one ('res.partner', placeholder="Driver Name",  domain="[('is_driver','=',True)]", string="Driver Name")        
    dwoid                       =fields.Char     (string ='DWO ID'      ,default='/',  readonly = True)   
    wono                        =fields.Char     (string="SO NO"        , readonly = True, Store=True )  
    claimid                     =fields.Char     (string="claimid"      , readonly = True, Store=True ) 
    invoiceno                   =fields.Char     (string="invoice NO"   , readonly = True, Store=True ) 
    draftselectable             =fields.Boolean  (string="selectable"   , readonly = True, Store=True) 
    chassisno                   =fields.Char     (string='No Rangka'    ,default='-') 
    engineno                    =fields.Char     (string='No Mesin'     ,default='-')   
    licenseplate                =fields.Char     (string='No polisi'     ,default='-')    
    carrier_name                =fields.Many2one ('tl.ms.dwocarrierinfo'    , string="Carrier Name (misal Fuso Fighter Fn 61)", placeholder="Carrier Info")        
    carrier_nopol               =fields.Char     (string='carrier No polisi', required=True, readonly = True, default='-')     
    @api.onchange('carrier_name')
    def onchange_carrier_name(self):   
        self.carrier_nopol = self.carrier_name.carriernopol 

    brandinfo                   =fields.Many2one ('tl.ms.dwobrandinfo'    ,  domain="[('manufacturer', '=', 'qi_brand')]", string="brand info")        
    # brandinfo                   =fields.Many2one ('tl.ms.dwobrandinfo'    , required=True, domain="[('manufacturer', '=', 'qi_brand')]", string="brand info")        
    currentlatitude             =fields.Char     ('current latitude ')
    currentlongitude            =fields.Char     ('current longitude')    
    manfactureyear              =fields.Char     (string='tahun dibuat' ,default='Not Available')  
    color                       =fields.Char     (string='warna'        ,default='Not Available')   
    peopletype                  =fields.Selection(string="Tipe"         ,  selection=[("DRVFRE", "Driver Freelance"), ("DRVFIX", "Driver Fixed") ])
    rp_driverimage              =fields.Binary   (string="image"        , Store=True) 
    rp_korlapimage              =fields.Binary   (string="image"        , Store=True) 
    rp_phone                    =fields.Char     (string='phone')   
    rp_mobile                   =fields.Char     (string='mobile')    
    rp_drivertype               =fields.Selection(string="Driver Tipe"      , selection=[("DRVFRE", "Driver Freelance"), ("DRVFIX", "Driver Fixed"),  ("OTHR", "Other") ])
    rp_alias                    =fields.Char     (string='alias') 
    senddate                    =fields.Datetime (string='Tanggal Kirim (saat estimasi driver mulai berangkat dari titik A ke B)'    , required=True)
    delivereddate               =fields.Datetime (string='Tanggal diterima (saat estimasi driver sampai ke titik B)'    , required=True)
    senddateactual              =fields.Datetime (string='Tanggal aktual Kirim (saat aktual driver mulai berangkat dari titik A ke B)'    , required=True)
    delivereddateactual         =fields.Datetime (string='Tanggal diterima (saat aktual driver sampai ke titik B)'    , required=True)
    @api.constrains('senddate', 'delivereddate')
    def _check_delivereddate(self):
        for record in self:
            if record.delivereddate < record.senddate:     
                raise ValidationError("Tanggal diterima tidak bisa lebih kecil dari Tanggal Kirim.") 
            
    dwodate                     =fields.Datetime (string='Tanggal Pengajuan',default=datetoday)
    msadditionalinfo            =fields.Many2one ('tl.ms.dwoadditionalinfo' , string='Additional info',  Required=True)   
    additionalinfo              =fields.Char     (string='Additional info (input SS customer name)', default='-')    
    quotationitemID             =fields.Char     (string="quotationitemID"  , Store=True , readonly=True)
    qi_brandcategory            =fields.Char     (string="brandcategory"    , Store=True , readonly=True) 
    qi_brand                    =fields.Char     (string="brand"            , Store=True)  
    qi_customerid               =fields.Char     (string="customerid"       , Store=True , readonly=True)
    qi_locationfrom             =fields.Char     (string="locationfrom"     , Store=True ) 
    qi_dropA_location           =fields.Char     (string="Drop A Location"  , Store=True ) 
    qi_locationto               =fields.Char     (string="locationto"       , Store=True ) 
    qi_salesprice               =fields.Float    (string="salesprice" )
    qi_cost                     =fields.Float    (string="cost(Uang Jalan)" , Store=True )  
    qi_discount                 =fields.Float    (string="discount"         , default=0, required=True)
    qi_salespriceafterdiscount  =fields.Float    (string='Final Price'      , default = 0, required=True) 
    qi_wayoftransport           =fields.Char     (string="wayoftransport"   , Store=True )
    qi_trip                     =fields.Char     (string="Trip"             , Store=True )
    qi_jenisbarang              =fields.Char     (string="Jenis Barang"     , Store=True )
    qi_jenistransaksi           =fields.Char     (string="Jenis Transaksi"  , Store=True )
    qi_usingferries             =fields.Boolean  (string="usingferries"     , Store=True )
    qi_multitrip                =fields.Many2many('tl.tr.draftwomultitrip'  , string="multi trip")
    qi_jenisunit                =fields.Char     (string="jenisunit"        , Store=True )
    dummy                       =fields.Char     (string=' '                , store=False, readonly = True) 
    # usedriver                   =fields.Boolean  (string="Use Driver") 
    drivername                  =fields.Char     (string='drivername')    
    driveridupload              =fields.Char     (string="Driver Name Upload")   
    donumber                    =fields.Char     (string="Do Number/BASTK"  , Required=True)   
    spe_number                  =fields.Char     (string="SPE Number"       , Required=[("qi_jenistransaksi",'=','LOG')])       
    wholesalename               =fields.Many2one ('tl.ms.wholesale'         , string='Nama Agen Logistic',  Required=[("qi_jenistransaksi",'=','LOG')])   
    drafttype                   =fields.Selection(string="Tipe Draft"       , default="DESTINATION",  selection=[("DESTINATION", "Destination Delivery Unit"),("DESTINATIONLOG", "Destination Logistic"), ("OTHER", "Other") ])
    salesdescription            =fields.Text     (string="Sale Description") 
    # qi_multitrip                =fields.Many2many('tl.tr.quotationitem.multitrip','tl_tr_draftwo_multitrip', string="multi trip")
    stage = fields.Selection(string="stage", default="NEW", 
            selection=[ ("NEW"       ,                                 "Newly Created"),
                        ("DRF"       ,                                         "Draft"),   
                        ("DIW"       ,                            "Draft in Workorder"),
                        ("RTC"       ,            "Ready To create uang jalan request"), 
                        ("DIC"       ,                           "Draft In Uang Jalan"),    
                        ("REQ-C/OP1" ,                    "Req App Uang Jalan OPS SPV"),
                        ("APV-C/OP1" ,                              "OPS SPV Approved"),
                        ("REQ-C/OP2" ,                    "Req App Uang Jalan OPS MGR"), 
                        ("APV-C/OP2" ,                              "OPS MGR Approved"),
                        ("REQ-C/FN1" ,                    "Req App Uang Jalan FNC SPV"),
                        ("APV-C/FN1" ,                              "FNC SPV Approved"), 
                        ("REQ-C/FN2" ,                    "Req App Uang Jalan FNC MGR"),
                        ("APV-C/FN2" ,                              "FNC MGR Approved"),  
                        ("APV-C/COM" ,                 "Approval Uang Jalan Completed"),   
                        ("CLAIMPAID" ,                      "Uang Jalan Has Been Paid"),   
                        ("PLOTREQ"   ,                        "Need Driver Allocation"),    #100
                        ("PLOTTED"   ,                       "Driver has been plotted"),    #200
                        ("MBL/DRVACC",                         "Driver Accepted Order"),    #400
                        ("MBL/DRVOTW",                "Driver is On the way(to Loc A)"),    #700
                        ("MBL/DRVLCA",                          "Driver on Location A"),    #800
                        ("MBL/DRVIPU",                                "Item Picked Up"),    #810
                        ("MBL/DRVLCB",                    "Item Dropped on Location B"),    #800
                        ("MBL/DRVDNE",                                    "Order Done"),    #900
                        ("DRVPJDONE" ,     "Driver telah pertanggungjawaban ke korlap"),    #new 
                        ("RTP"       ,           "Ready To create Pertanggung Jawaban"),    
                        ("DIP"       ,                  "Draft in Pertanggung Jawaban"),     
                        ("REQ-PJ/OP1",            "Req App Pertanggungjawaban OPS SPV"),
                        ("APV-PJ/OP1",                              "OPS SPV Approved"),
                        ("REQ-PJ/OP2",            "Req App Pertanggungjawaban OPS MGR"), 
                        ("APV-PJ/OP2",                              "OPS MGR Approved"),
                        ("REQ-PJ/FN1",            "Req App Pertanggungjawaban FNC SPV"),
                        ("APV-PJ/FN1",                              "FNC SPV Approved"), 
                        ("REQ-PJ/FN2",            "Req App Pertanggungjawaban FNC MGR"),
                        ("APV-PJ/FN2",                              "FNC MGR Approved"),  
                        ("APV-PJ/COM",         "Approval Pertanggungjawaban Completed"),   
                        ("PJPAID"    , "Selisih Uang Pertanggungjawaban Has Been Paid"),   
                        ("PJRTD"     ,       "Pertanggungjawaban Ready To Dynamic 365"),    
                        ("RTI"       ,                          "Ready To be Invoiced"), 
                        ("OCI"       ,                           "Occupied in Invoice")]) 
 
    activestage =fields.Selection(string="active stage", default="ACT", 
            selection=[ ("ACT",  "Active                                  "   ),
                        ("CDR",  "Canceled in draftwo    stage            "   ),
                        ("CWO",  "Canceled in workorder  stage            "   ),
                        ("CIC",  "Canceled in Uang Jalan stage            "   ),
                        ("CIO",  "Canceled while order is being delivered "   ),
                        ("CIP",  "Canceled in Pertanggungjawaban stage    "   ),
                        ("CIV",  "Canceled in Invoice    stage            "   ),
                        ("CLS",  "Closed, successful transaction          "   )
                       ])
    triptype = fields.Selection(string="tipe kirim", default='KIRIM', selection=[ ("KIRIM",  "Kirim"),("TARIK",  "Tarik")]) 
     
    claimid =fields.Char(string="nomor claim")
    claimamount =fields.Float(string="amount diajukan", default=0)
    pjid =fields.Char(string="nomor pertanggungjawaban")
    claimaccountabilityamount =fields.Float(string="Jumlah Pemakaian Real", default=0)
    # claimaccountabilityamount =fields.Float(string="Jumlah Pemakaian", default=0, required=True)
     
    def getdefaultaccountability(self):
        money = 1000
        return money
    def name_get(self):
        result = [] 
                    
        for s in self:  
            name ='' 
            fdt=False
            a = s.customerid.companyinitial ; b = s.qi_cost ; c = s.qi_trip ; d = s.qi_jenistransaksi; e = s.triptype; f = s.quotationitem
            if(a in(None, False)): a= '[--]'
            if(b in(None, False)): b= 0
            if(c in(None, False)): c= '[--]'
            if(d in(None, False)): d= '[--]' 
            else: d+ ' TRIP'
            if(e in(None, False)): e= '[--]' 
            if(f in(None, False)): f= '[--]'
            else: 
                f=f.multitrip
                for id in f: 

                    if(fdt!=False): fdt = fdt + '>>' +id.locationfrom.locationname 
                    else          : fdt = id.locationfrom.locationname 

            if(fdt in(None, False)): fdt= '[--]'
            name = 'DFT/'+a+'/'+e+'/'+d+'/'+f"{int(b):,}" +'/'+c +fdt
            result.append((s.id,name)) 

        return result 

    @api.onchange('msadditionalinfo')
    def onchange_msadditionalinfo(self):   
        self.additionalinfo = self.msadditionalinfo.additionalinfo#self.driverid.image_field_name  
 

    @api.onchange('driverid')
    def _onchange_driverid_validation(self):    
        self.drivername = self.driverid.name        ; self.rp_driverimage   = self.driverid.image_128 
        self.rp_phone   = self.driverid.phone       ; self.rp_korlapimage   = self.driverid.korlap.image_128 
        self.rp_mobile  = self.driverid.mobile      ; self.rp_drivertype    = self.driverid.drivertype 
        # self.korlapid   = self.driverid.korlap.name ; self.rp_alias         = self.driverid.driveralias 
        self.rp_alias   = self.driverid.driveralias 
 
    
    def default_temp(self):
        dwoid_temp=''
        if(self.dwoid_temporary== False): 
            cinint= self.customerid.companyinitial 
            dwoid_temp = self.env['ir.sequence'].sudo().get_per_doc_code(cinint, 'DWOTEMP')    
        else:
            dwoid_temp =self.dwoid_temporary
        return dwoid_temp 
       
             
    @api.onchange('quotationitem')
    def _onchange_quotationitem_validation(self):  
        if(self.dwoid_temporary in (False, None)): self.dwoid_temporary = self.default_temp() 
        x = self.quotationitem
        self.qi_usingferries = x.usingferries    ;self.qi_brand         = x.brand          ; self.quotationitemID      = x.quotationitemid 
        self.qi_cost         = x.cost            ;self.qi_brandcategory = x.brandcategory  ; self.qi_customerid        = x.customerid 
        self.qi_salesprice   = int(x.salesprice) ;self.qi_trip          = x.pilihtrip      ; self.qi_wayoftransport    = x.wayoftransport    
        a = x.locationfrom;  a1 = x.dropA_location;  b = x.locationto
        if(a ==False): a = x.M2O_locationfrom.locationname
        if(a1==False): a1= x.dropA_M2O_location.locationname
        if(b ==False): b = x.M2O_locationto.locationname
        self.qi_locationfrom=a; self.qi_dropA_location = a1; self.qi_locationto  =b
        multi_quot = x.multitrip ; multicount = 0
        for id in multi_quot: multicount =multicount+1         
        tl_tr_draftwomultitrip = self.env['tl.tr.draftwomultitrip'].sudo().search([('dwoid_temp', '=', self.dwoid_temporary)])
        tl_tr_draftwomultitrip.sudo().unlink()  
        if(multicount == 0): print('disini multicount 0')       
        if(multicount >  0):      
            dict_temp={}; data_temp =[]; dwomulticount = 0 ;data_id =[] ; data_hd =[]; data_cover =[]
            for id in tl_tr_draftwomultitrip:  dwomulticount = dwomulticount+1    
            for content in multi_quot       :  tl_tr_draftwomultitrip.sudo().create({'dwoid_temp': self.dwoid_temporary, 'dwoid': self.dwoid, 'quotationitemID': x.quotationitemid, 'dwo_sequence': content.sequence, 'dwo_locationfrom'  : content.locationfrom.locationname , 'dwo_loadtype': content.loadtype, 'dwo_item_load': content.item_load.itemname, 'dwo_item_unload'   : content.item_unload.itemname , 'loadtime': False,'unloadtime': False})                 
            tl_tr_draftwomultitrip          =  self.env['tl.tr.draftwomultitrip'].sudo().search([('dwoid_temp', '=', self.dwoid_temporary),('dwoid_temp', '!=', False)]) 
            ctthis = 0
            for id in tl_tr_draftwomultitrip:  ctthis = ctthis+1; data_id.append(id.id)
            data_hd.append(6) ; data_hd.append(False) ; data_hd.append(data_id) ; data_cover.append(data_hd); self.qi_multitrip =data_cover 
                    
        self.qi_jenisunit       = x.jenisunit  ; self.qi_jenistransaksi  = x.jenistransaksi
        a = self.qi_jenistransaksi
        if(  a=="DU" ): self.qi_jenisbarang   = x.jenisbarangDU
        elif(a=="LOG"): self.qi_jenisbarang   = x.jenisbaranglogistic
        self.salesdescription =self.getsalesdescription()
     
        the_domain = self.branddomain()
        return the_domain

    def getsalesdescription(self):
        a='' ;  a1='' ; b=''; c=''; d='' ; e=''; f='';g=''

        output = ''
        if(self.quotationitem.quotationitemid == 'False'):  output = ''
        else: 
            if(self.qi_locationfrom  !=False):a = 'From:'    +str(self.qi_locationfrom    )+' '
            if(self.qi_dropA_location!=False):a1= 'Drop A:'  +str(self.qi_dropA_location  )+' '
            if(self.qi_locationto    !=False):b = 'To:'      +str(self.qi_locationto      )+' ' 
            if(self.qi_cost          !=False):d = '/Cost:'   +str(int(self.qi_cost       ))+' '
            if(self.qi_brand         !=False):e = '/Brand:'  +str(self.qi_brand           )+' '
            if(self.brandinfo        !=False):f = ''         +str(self.brandinfo.brandname)+' '
            if(self.drafttype        !=False):g = ''         +str(self.drafttype)
            if(g=='DESTINATION')     :g='Delivery Unit:'
            if(g=='DESTINATIONLOG')  :g='Delivery Logistic:'
            if(g=='OTHER')           :g='Tagihan Lain-Lain:'
            output   = g+a+a1+b+c+d+e+f
        if(str(self.drafttype) =='OTHER'): output   = None
        return output 
        
    @api.onchange('brandinfo')
    def onchange_brandinfo(self):   
        self.salesdescription = self.getsalesdescription() 
        

        
    def branddomain(self): 
        if(self.qi_brand): 
            brands = self.env['tl.ms.productbrand'].search([('manufacturer', '=', self.qi_brand)])  
            overalldomain   =  [('manufacturer', 'in', brands.ids)] ;  
            the_domain = False
            if(overalldomain):
                the_domain = {'domain': {'brandinfo':overalldomain }} 
            # self.brandinfo = False
            return  the_domain
    
 
    @api.onchange('qi_salespriceafterdiscount')
    def _onchange_salespriceafter(self): self.recalculate()
    @api.onchange('qi_discount')
    def _onchange_discount(self)       : self.recalculate()
    @api.onchange('qi_salesprice')
    def _onchange_salesprice(self)     : self.recalculate()
 
    def recalculate(self):    
        for record in self:  
            a=record['qi_salesprice'] ; b=record['qi_discount'] ; record['qi_salespriceafterdiscount'] =a-b
    
    # start pilihan draftwo
    @api.onchange('drafttype')
    def action_reloaddrafttype(self):  
        jenistransaksi = '' 

        for rec in self:
            if(str(rec.drafttype) !='None'):
                if(str(rec.drafttype) =='DESTINATION'):
                    jenistransaksi="DU"
                    print('self.usedriver=True')
                if(str(rec.drafttype) =='DESTINATIONLOG'):
                    jenistransaksi="LOG"
                    print('self.usedriver=True')
                if(str(rec.drafttype) =='OTHER'):  
                    rec.quotationitem       =None;  rec.quotationitemID     =None;  rec.qi_brandcategory    =None;  rec.qi_brand            =None
                    rec.qi_customerid       =None;  rec.qi_locationfrom     =None;  rec.qi_dropA_location   =None;  rec.qi_locationto       =None;  rec.chassisno           =None 
                    rec.engineno            =None;  rec.manfactureyear      =None;  rec.color               =None;  rec.salesdescription    =None 
        the_domain = self.quotationdomain()
        return the_domain
        
         

    @api.onchange('dwoid','wono','invoiceno','customerid','custinitial','chassisno','engineno','senddate','manfactureyear','color','peopletype','driverid','quotationitem','quotationitemID','drafttype','salesdescription')
    def all_onchange(self):  
        if(self.stage=='NEW'):
            self.stage ='DRF' 
 

    def revertdraft(self): #disini setiap row akan do the  defwrite. semakinbanyak  row di action,  semakin sering  defwrite
        self.stage ='DRF' 
        self.activestage ='ACT' 
    def reactivate(self):
        # if(self.activestage in())
        if (self.stage in("RTC","DIC","RTP","DIP") and self.activestage in("CIC","CIP","CWO")):
            self.activestage = 'ACT' #do a defwrite
        else:
            msg = "mohon maaf saat ini yang dapat di reactivate hanya yang berstatus"
            msg = msg+ "Draft in Claim[DIC], Ready To Claim[RTC]"
            msg = msg+' dan activestage Canceled in Claim [CIC]. sisanya akan enhance kemudian'
            msg = msg+'status saat ini. stage=['+str(self.stage)+'], activestage = ['+str(self.activestage)+']'
            raise ValidationError(msg)   
           
        
    def write(self, vals):   
        msg =''     
        drafttype = vals.get('drafttype') 
        self.qi_multitrip.filtered(lambda r: r.dwoid != self.dwoid).write({'dwoid': self.dwoid})
        actfrom ='tl_tr_draftwo def write:multitrip not found';actto=actfrom; actdropA=actfrom
        qi_multitrip_records = self.env['tl.tr.draftwo'].sudo().search([('dwoid', '=', self.dwoid)]).qi_multitrip
        sorted_records       = sorted(qi_multitrip_records, key=lambda r: r.dwo_sequence)
        x = len(qi_multitrip_records)
        if   x== 3: 
            actfrom =sorted_records[0].dwo_locationfrom
            actdropA=sorted_records[1].dwo_locationfrom
            actto   =sorted_records[2].dwo_locationfrom
        elif x== 2: 
            actfrom =sorted_records[0].dwo_locationfrom 
            actdropA=False
            actto   =sorted_records[1].dwo_locationfrom
        elif x== 1: 
            actfrom =sorted_records[0].dwo_locationfrom
            actdropA=False
            actto   =actfrom
        else:
            raise ValidationError('tl_tr_draftwo.py defwrite. xx001')   
        if 'qi_locationfrom'    not in vals: vals['qi_locationfrom']   = actfrom
        if 'qi_dropA_location'  not in vals: vals['qi_dropA_location'] = actdropA
        if 'qi_locationto'      not in vals: vals['qi_locationto']     = actto   
        for f in self:
            stagefrom =f.stage  
            stageto = vals.get('stage')
            if(stageto==False or stageto ==None): 
                stageto = stagefrom 
            isupdatestage = True; allowedupdate = True
            if(stagefrom == None or  stageto  == None):
                isupdatestage=False  
            if(stagefrom=='DRF'                      and stageto =='NEW'): a='ok boleh'
            if(stagefrom in('NEW','DRF','CIV','CWO') and stageto =='DRF'): a='ok boleh'
            if(stagefrom in('DIW'                  ) and stageto =='RTC'): a='ok boleh'#disini
            else:
                allowedupdate = False
                msg = '[tl.tr.draftwo]status sudah bukan di NEW atau DRAFT, tidak bisa di edit lagi. stagefrom='+stagefrom+', stageto:'+stageto 
            if(self.customerid.id != False and self.quotationitem.customerid.id !=False and drafttype !=None):
                if(self.customerid  != self.quotationitem.customerid):
                    allowedupdate=False
                    msg="anda memilih customer="""+self.customerid.name+"""  sementara pilihan quotation yang anda pilih  itu milik customer="""+self.quotationitem.customerid.name+""" """
            res = super(draftwo, self).write(vals)
            if(isupdatestage or allowedupdate):  
                x =self.env['tl.tr.draftwomultitrip'].sudo().search([('dwoid_temp', '=', self.dwoid_temporary)]) ; dwomultitripct  =0
                for id in x: dwomultitripct = dwomultitripct+1  
                if(dwomultitripct>0): x.write({'dwoid':self.dwoid})  
                return res
            else:
                raise ValidationError(msg)   
         
         
 
    @api.model
    def create(self, vals):     
        msg = ''
        table_driver = False   ; table_customer = False
        vals_remake ={'korupsi': 'gas'  } 
        isupload= vals.get('isupload');  isforminput= vals.get('isforminput')  
        if(isupload ==None and isforminput==None): raise ValidationError('data input kehilangan identitas, apakah ini data input, atau upload? jika anda menemukan error ini pada saat upload.. pastikan di excel, column A1 = ISUPLOAD, dan content dibawahnya adalah  TRUE')
        if(isupload ==False and isforminput==None): raise ValidationError('pastikan di excel, column A1 = ISUPLOAD, dan content dibawahnya adalah  TRUE, bukannya ('+str(isupload)+') seperti  yang anda masukkan')
        
        if(isupload): 
            print('isupload masuk')        
            mandatory_header = [  'triptype'  ,'drafttype'	,  'customerid'		  ]  
                
            tipekirim       = vals.get('triptype')       ; drafttype = vals.get('drafttype')
            additionalinfo  = vals.get('additionalinfo') ; chassisno = vals.get('chassisno') ;    engineno      = vals.get('engineno')
            manfactureyear  = vals.get('manfactureyear') ; color     = vals.get('color')     ;    dwodate       = vals.get('dwodate')             
            senddate        = vals.get('senddate')       ; custid    = vals.get('customerid');    quotationitem = vals.get('quotationitem')     
            drivername      = vals.get('driveridupload') 
            drivername      = str(drivername)

            tbldriver =self.env['res.partner'].search([('is_driver', '=', True),('name', '=', drivername)]) 
            if(len(tbldriver) < (       1       ))  :   raise ValidationError('data driver dengan nama isupload'+str(isupload)+'drivername:'+str(drivername)+' tidak ditemukan')
            if(len(tbldriver) > (       1       ))  :   raise ValidationError('data driver dengan nama '+str(drivername)+' ada banyak ditemukan. diskusi dengan IT bagaimana penyelesaiannya') 
            if(custid    ==     (     False     ))  :   raise ValidationError('data customer tidak ditemukan')     
            if(tipekirim not in ('TARIK','KIRIM'))  :   raise ValidationError('TIPE KIRIM ['+str(tipekirim)+'] not found') 
            if(drafttype !=     ( 'DESTINATION' ))  :   raise ValidationError('drafttype  ['+str(drafttype)+'] is not valid,  we only accept DESTINATION') 
            # if(dwodate   in     (None, False    ))  :   raise ValidationError('tanggal pengajuan is not valid,  tidak boleh kosong') 
            if(senddate  in     (None, False    ))  :   raise ValidationError('tanggal kirim is not valid,  tidak boleh kosong') 
 
            table_customer          =self.env['res.partner'         ].search([('id', '=', custid        ),('is_company', '=', True              ),('is_logistic_customer', '=', True)], limit=1) 
            table_driver            =self.env['res.partner'         ].search([('id', '=', tbldriver.id  ),('is_company', '=', False             ),('is_driver'           , '=', True)], limit=1) 
            table_existingquotation =self.env['tl.tr.quotationitem' ].search([('id', '=', quotationitem ),('customerid', '=', table_customer.id )], limit=1) 
             
            header_fields = [] ; dict ={} ; data =[]
 
            for mandatory_field in mandatory_header: 
                if not vals.get(mandatory_field,False): header_fields.append(mandatory_field)  
            if len(header_fields) > 0: 
                info = "import data MAM missing required data in header %s" %str(header_fields) 
                dict={'Status':'false','Message':info}; data.append(dict); msg= json.dumps(data) ; raise ValidationError(msg)    
            else:      
                vals_remake = {
                    'stage'                     : 'DRF', 'activestage': 'ACT',            'customerid'                : table_customer.id,
                    'custinitial'               : table_customer.companyinitial,          'drafttype'                 : drafttype,
                    'additionalinfo'            : additionalinfo,                         'chassisno'                 : chassisno,
                    'engineno'                  : engineno,                               'manfactureyear'            : manfactureyear,
                    'color'                     : color,                                   
                    'driverid'                  : table_driver.id,                        'triptype'                  : tipekirim,
                    'dwodate'                   : dwodate,                                'senddate'                  : senddate, 
                    'quotationitem'             : table_existingquotation.id,             'quotationitemID'           : table_existingquotation.quotationitemid , 
                    'qi_brandcategory'          : table_existingquotation.brandcategory,  'qi_brand'                  : table_existingquotation.brand,  
                    'qi_locationfrom'           : table_existingquotation.locationfrom,   'qi_dropA_location'         : 'gak tau ini diisi apa.',    
                    'qi_locationto'             : table_existingquotation.locationto,     'qi_wayoftransport'         : table_existingquotation.wayoftransport,         
                    'qi_usingferries'           : table_existingquotation.usingferries,   'qi_salespriceafterdiscount': table_existingquotation.salespriceafterdiscount,
                    'rp_phone'                  : table_driver.phone,                     '__last_update'             : False,                                          
                    'rp_mobile'                 : table_driver.mobile,                    'rp_drivertype'             : table_driver.drivertype,                        
                    'rp_alias'                  : table_driver.driveralias,    
                    'salesdescription'          : 'From   :'+str(table_existingquotation.locationfrom)+' To    :'+str(table_existingquotation.locationto  )+
                                                  ' /Price:'+str(table_existingquotation.salesprice  )+' /Cost :'+str(table_existingquotation.cost        )+
                                                  ' /Brand:'+str(table_existingquotation.brand       )
                            }  
                res = super(draftwo, self).create(vals_remake)
                return res
        if(isforminput): 
            mandatory_header= [  'triptype'  ,'drafttype'			  ]  
            header_fields   = [] ; dict ={} ; data =[]   
            for mandatory_field in mandatory_header: 
                if not vals.get(mandatory_field,False): header_fields.append(mandatory_field)  
            if len(header_fields) > 0:
                info = "import data MAM missing required data in header %s" %str(header_fields) 
                dict={'Status':'false','Message':info}; data.append(dict); msg= json.dumps(data) ; raise ValidationError(msg)
            else: 
                inputan_customerid  =vals.get('customerid');  
                table_customer      =self.env['res.partner'].search([('id', '=', inputan_customerid)], limit=1) 
                vals['custinitial'] =table_customer.companyinitial
                
                if( vals.get('custinitial') in(False,None) ):
                    defaultcus          = self.env['tl.ms.user'].search([('user_id', '=', self.env.user.id)], limit=1)   
                    vals['custinitial'] = defaultcus.defaultcustomer.companyinitial 

                c_initial =   vals.get('custinitial')
                if(c_initial in (False,None)): raise ValidationError('data cust initial tetap tidak ditemukan')
                inputan_quotationitem = vals.get('quotationitem')
                if(vals.get('drafttype')!='OTHER' and inputan_quotationitem in (False,None)): raise ValidationError('data quotationitem tidak ditemukan')
                table = self.env['tl.tr.quotationitem'].sudo().search([('id','=',inputan_quotationitem)])
                if(vals.get('qi_salesprice' ) in(0,False,None)):   vals['qi_salesprice'] =table.salesprice
                if(vals.get('qi_cost'       ) in(0,False,None)):   vals['qi_cost']       =table.cost
                if(vals.get('qi_discount'   ) in(0,False,None)):   vals['qi_discount']   =table.discount 
         
                inputan_cost        = vals.get('qi_cost')
                inputan_salesprice  = vals.get('qi_salesprice')
                inputan_discount    = vals.get('qi_discount')

                vals['qi_salespriceafterdiscount'] =inputan_salesprice-inputan_discount
                if(inputan_cost>inputan_salesprice): raise ValidationError("cost "+str(inputan_cost)+" tidak boleh lebih tinggi dari salesprice"+str(inputan_salesprice))  
                if(table_customer.id != table.customerid.id):
                    pilihan_custid = table_customer.name 
                    quot_custid = table.customerid.name
                    if(vals.get('drafttype')!='OTHER'): 
                        msg ="anda memilih customer="""+pilihan_custid+"""  sementara pilihan quotation yang anda pilih  itu milik customer="""+quot_custid+""" """
                        raise ValidationError(msg)
                the_dwoid = self.env['ir.sequence'].get_per_doc_code(c_initial, 'DWO') 
                vals['dwoid'] = the_dwoid
                x =self.env['tl.tr.draftwomultitrip'].sudo().search([('dwoid_temp', '=', vals.get('dwoid_temporary'))]) ; dwomultitripct  =0 
                 
                for id in x: dwomultitripct = dwomultitripct+1  
                if(dwomultitripct>0): x.write({'dwoid':vals.get('dwoid')}) 
                res = super(draftwo, self).create(vals)
                return res


    @api.model
    def unlink(self, vals):  
        for item in vals:  
            table = self.env['tl.tr.draftwo'].sudo().search([('id','=',item)]) 
            stage =  table.stage 
            if(stage!="DRF" and stage!="NEW"):
                errmsg = "kamu gak bisa hapus draftwo kecuali dalam status DRAFT, dan hanya akan berubah ke status CANCELED"+str(stage)
                if(stage=="CDR" or table.activestage=="CDR"):
                    errmsg="ini sudah berstatus cancel"
                raise ValidationError(errmsg)   
            else: 
                query = """ update tl_tr_draftwo set stage = 'CDR', WONO =NULL, INVOICENO=NULL where id  in("""+str(item)+""") """ 
                self._cr.execute(query)  
                table.sudo().write({'activestage':'CDR','WONO':False, 'INVOICENO':  False})  
                           
                 
                           
                # (0, 0,  { values })    link to a new record that needs to be created with the given values dictionary
                # (1, ID, { values })    update the linked record with id = ID (write *values* on it)
                # (2, ID)                remove and delete the linked record with id = ID (calls unlink on ID, that will delete the object completely, and the link to it as well)
                # (3, ID)                cut the link to the linked record with id = ID (delete the relationship between the two objects but does not delete the target object itself)
                # (4, ID)                link to existing record with id = ID (adds a relationship)
                # (5)                    unlink all (like using (3,ID) for all linked records)
                # (6, 0, [IDs])          replace the list of linked IDs (like using (5) then (4,ID) for each ID in the list of IDs)
           