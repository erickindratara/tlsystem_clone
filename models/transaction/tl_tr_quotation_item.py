from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from gettext import translation 
from odoo.http import Response, request
from odoo import http  
from io import BufferedRandom
from tokenize import ContStr
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from xml.etree.ElementTree import fromstring
from odoo import api, fields, models 
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta 


class loaditem(models.Model): #
    _name               = 'tl.ms.loaditem' 
    _description        = 'master load item'  
    _rec_name           = 'itemname'
    itemname            = fields.Char(string='Nama Barang' )    
    
 
class draftwomultitrip(models.Model): #
    _name = 'tl.tr.draftwomultitrip' #nama di db berubah jadi training_course
    _description = 'Transaction Draft WO multitrip' 
    # _rec_name = 'dwo_sequence'    
  
    dwoid_temp              = fields.Char    (  string ='DWO ID temp'    )   
    dwoid                   = fields.Char    (  string ='DWO ID'         )   
    quotationitemID         = fields.Char    (  string ='quotationitemID')   
    dwo_sequence            = fields.Integer (  string="sequence"        ) 
    dwo_locationfrom        = fields.Char    (  string="locationfrom"    ) 
    dwo_latitude            = fields.Char    (  string="latitude"        ) 
    dwo_longitude           = fields.Char    (  string="longitude"       ) 
    dwo_alamat              = fields.Char    (  string="alamatlengkap"   ) 
    dwo_loadtype            = fields.Char    (  string="loadtype"        )          
    dwo_item_load           = fields.Char    (  string="barang muat"     )
    dwo_item_unload         = fields.Char    (  string="barang bongkar"  )  
    loadtime                = fields.Datetime(  string="waktu selesai muat"    , required=False)
    unloadtime              = fields.Datetime(  string="waktu selesai bongkar" , required=False) 
    @api.model
    def create(self, vals):   
        res = super(draftwomultitrip, self).create(vals)
        return res
    
class quotationitemmultitrip(models.Model): #
    _name                = 'tl.tr.quotationitem.multitrip' 
    _description         = 'Transaction quotationitem multitrip' 
    _order               = 'sequence'
    _rec_name            = 'locationfrom'
    sequence             = fields.Integer    ('sequence'              , help="Sequence for the handle.",default=1) 
    sequenceview         = fields.Integer    ('sequence'              , help="Sequence for the view.",default=1) 
    quotationitem        = fields.Many2one   ('tl.tr.quotationitem'   , string="quotationitem" )
    quotationitemid      = fields.Char       ('quotationitemid'       , help="quotation") 
    locationfrom         = fields.Many2one   ('tl.ms.customerlocation', string='From')   
    locationfromlatitude = fields.Char('latitude (diinput di mobile app oleh korlap)')   
    locationfromlongitude= fields.Char('longitude (diinput di mobile app oleh korlap)')    
    locationfromalamat   = fields.Char('Alamat')     
    loadtype             = fields.Selection  (string="bongkarmuat", selection=[("BONGKAR",  "Bongkar"),("MUAT",  "Muat"),("BONGKARMUAT",  "Bongkar Muat"),("DU",  "Delivery Unit") ]) 
    item_load            = fields.Many2one('tl.ms.loaditem', string='barang muat') 
    item_unload          = fields.Many2one('tl.ms.loaditem', string='barang bongkar') 
    update_id            = fields.Char       ('update_id') 
     
    @api.onchange('sequence')
    def onc_squence(self): 
        x = self.env['tl.tr.quotationitem.multitrip'].sudo().search([('id', '=', self._origin.id)])   
        x.sudo().write({'sequence':self.sequence,'sequenceview' :self.sequence })
       

    def cekdefaultfilter(self):  
        ir_filters = self.env['ir.filters'].sudo(); ir_filters.search([('model_id', '=', 'tl.tr.quotationitem.multitrip')]).sudo().unlink()  
        ir_filters.sudo().create({ 
            'name'      :"stage in New, Draft. Group by Send Date"   ,'domain'    : '[]'  ,'context'   : "[]",'is_default': 'True',
            'model_id'  : 'tl.tr.quotationitem.multitrip'            ,'active'    : 'True','sort'      : "[{'order_by': ['locationfrom']}]"  }    )

    @api.onchange('loadtype')
    def loadtype_onchange(self): 
        if(self.loadtype not in(False,None)): 
            ltype = self.loadtype; nullid=self.createitem_na()
            if(ltype =='BONGKAR'):self.item_load   = nullid  ; self.item_unload = None  
            if(ltype =='MUAT'   ):self.item_unload = nullid  ; self.item_load   = None  
            if(ltype =='DU'     ):self.item_load   = nullid  ; self.item_unload = nullid  
    
    def createitem_na(self): 
        nulltext = 'n/a'; nullid=0
        load = self.env['tl.ms.loaditem'].search([('itemname', '=', nulltext)], limit=1) 
        if(load.id in(None, False)):   
            vals = {'itemname'   :nulltext,} ; self.env['tl.ms.loaditem'].sudo().create(vals )  
        load = self.env['tl.ms.loaditem'].search([('itemname', '=', nulltext)], limit=1) 
        return load.id

    def write(self, vals):  
        res =[]  
        for r in self:   
            print(self.sequence,'xxxxxxxxxxxxx',vals) 
        res = super(quotationitemmultitrip, self).write(vals) 
        return  res
    
    def create(self, vals):    
        record =super(quotationitemmultitrip, self).create(vals) 
        self.env.cr.commit()   
        return  record 
    
class quotationitem(models.Model): #
    _name               = 'tl.tr.quotationitem' #nama di db berubah jadi training_course
    _description        = 'Transaction quotationitem' 
    _rec_name           = 'quotationitemid'
    _inherit            = 'tl.tr.quotationitem.multitrip'
    # print_handle_ids = fields.Many2many('sale.order.handle','sale_handle','order_id','order_handle_id','Many2many order')
    ismultitrip         = fields.Selection(string="trip",  selection=[("NOTRIP",  "No Trip"),("INCOMPLETE",  "Incomplete Trip"),("SINGLE",  "Single Trip"), ("MULTI",  "Multi Trip"), ("OVERLOADTRIP",  "Too Much Trip, please reduce the trip")]) 
     
    def createitem_na(self):
        nulltext = 'n/a'; nullid=0
        load = self.env['tl.ms.loaditem'].search([('itemname', '=', nulltext)], limit=1) 
        if(load.id in(None, False)):   
            vals = {'itemname'   :nulltext,} ; self.env['tl.ms.loaditem'].sudo().create(vals )  
            load = self.env['tl.ms.loaditem'].search([('itemname', '=', nulltext)], limit=1) 
        return load.id 
    
    pilihtrip              = fields.Selection(string="trip", default="SINGLE",  selection=[("SINGLE",  "Single drop"),("MULTI",  "Multi drop")])  
    
    def get_selection_options(self):
        return [("BONGKAR", "Bongkar"),("MUAT", "Muat"),("BONGKARMUAT", "Bongkar Muat"),("DU", "Delivery Unit")]

    M2O_locationfrom       = fields.Many2one('tl.ms.customerlocation' , string="locationfrom" ,  required=True)
    locationfrom           = fields.Char(     string="locationfrom")   
    sgl_loadtype_fr        = fields.Selection(string="bongkarmuat"  , required=False, selection=get_selection_options) 
    sgl_item_load_fr       = fields.Many2one ('tl.ms.loaditem'      , required=False , default = createitem_na, string='barang muat') 
    sgl_item_unload_fr     = fields.Many2one ('tl.ms.loaditem'      , required=False , default = createitem_na, string='barang bongkar') 
    
    dropA_M2O_location     = fields.Many2one('tl.ms.customerlocation' , string="drop A"   )
    dropA_location         = fields.Char(     string="location drop A")
    dropA_sgl_loadtype     = fields.Selection(string="bongkarmuat"  , required=False , selection=get_selection_options) 
    dropA_sgl_item_load    = fields.Many2one ('tl.ms.loaditem'      , required=False , default = createitem_na, string='barang muat') 
    dropA_sgl_item_unload  = fields.Many2one ('tl.ms.loaditem'      , required=False , default = createitem_na, string='barang bongkar') 
    
    M2O_locationto         = fields.Many2one('tl.ms.customerlocation' , string="locationto"   ,  required=True)
    locationto             = fields.Char(     string="locationto")   
    sgl_loadtype_to        = fields.Selection(string="bongkarmuat"  , required=False , selection=get_selection_options) 
    sgl_item_load_to       = fields.Many2one ('tl.ms.loaditem'      , required=False , default = createitem_na, string='barang muat') 
    sgl_item_unload_to     = fields.Many2one ('tl.ms.loaditem'      , required=False , default = createitem_na, string='barang bongkar') 
    
    
    # ismultitriptoggle   = fields.Boolean(string="Input Banyak Trip?") 
    jenisbaranglogistic = fields.Selection(string="jenis barang", selection=[("ALATBERAT",  "Alat Berat"),("FROZEN"     , "Barang Beku"),("HASILTANI"     ,  "Hasil Pertanian"),
                                                                             ("KARGOUMUM",  "Kargo Umum"),("FRAGILE"    , "Pecah Belah"),("PRODUKKEMASAN" ,  "Produk Kemasan" ),
                                                                             ("OTHER"    ,  "Lainnya"   ),("MOBILMOTOR" , "Mobil/Motor")]) 
    jenisbarangDU       =   fields.Selection(string="jenis barang"   , selection=[("MOBILMOTOR",  "Mobil/Motor")]) 
    jenistransaksi      =   fields.Selection(string="jenis Transaksi", selection=[("LOG",  "Logistic"),("DU",  "Delivery Unit")]) 
    jenisunit           =   fields.Selection(string="jenis unit"     , selection=[("CDD",  "CDD"),("WB",  "WB"),("CDE",  "CDE")])  
    # rekaptrip           =   fields.Text(string="rekap trip") 

    @api.onchange('jenistransaksi','pilihtrip')
    def jenistransaksi_onchange(self):   
        a = self.pilihtrip
        if(a in (None, False)): a = 'SINGLE'
        
        item_n_a = self.getitem_na()
         
        self.jenisbaranglogistic    = None;  self.jenisbarangDU = None      ;  self.brand = None;  self.M2O_brand  = None; 
        self.multitrip              = None;  self.ismultitrip   = 'NOTRIP'
        if(self.jenistransaksi =='LOG'): self.wayoftransport = "TRUCKING" ;self.jenisbaranglogistic  ="OTHER"       
        if(self.jenistransaksi =='DU' ): self.wayoftransport = "SELFDRIVE";self.jenisbarangDU        ="MOBILMOTOR"  
        if(a=='SINGLE'):
            self.dropA_M2O_location  =False; self.dropA_sgl_loadtype   =False
            self.dropA_sgl_item_load =False; self.dropA_sgl_item_unload=False
            if(self.jenistransaksi =='LOG'):  self.sgl_loadtype_fr ="MUAT"  ;self.sgl_loadtype_to     ="BONGKAR"
            if(self.jenistransaksi =='DU' ):  self.sgl_loadtype_fr ="DU"    ;self.sgl_loadtype_to     ="DU"
        if(a=='MULTI'):
            self.dropA_M2O_location  =False;  
            self.dropA_sgl_item_load =item_n_a; self.dropA_sgl_item_unload=item_n_a
            if(self.jenistransaksi =='LOG'):  self.sgl_loadtype_fr ="MUAT"; self.dropA_sgl_loadtype="BONGKARMUAT"; self.sgl_loadtype_to ="BONGKAR"
            if(self.jenistransaksi =='DU' ):  self.sgl_loadtype_fr ="DU"  ; self.dropA_sgl_loadtype ="DU"        ; self.sgl_loadtype_to ="DU"
            
        

    #coding customer id start 
         
 
    @api.onchange('customerid') #disini
    def cus_onchange(self):    
        cinitial = ''
        if(self.customerid!=None and self.customerid.id != 'False'):
            cinitial = self.customerid.companyinitial ; self.custinitial = cinitial
            self._cr.execute( """ update tl_ms_user set defaultcustomer =  '"""+str(self.customerid.id)+"""'  where user_id = '"""+str(self.env.user.id)+"""' """)
        

        tblcustomer  = self.env['res.partner'].search([('id', '=', self.customerid.id)], limit=1)    
        if(tblcustomer.name  in('PT Surya Sudeco','PT Tunas Mobilindo perkasa')):
            self.jenistransaksi ="DU"
            self.jenisbarangDU="MOBILMOTOR"
        else:
            self.jenistransaksi ="LOG" 
        for rec in self: 
            rec.write({'locationto': [(5, 0, 0)],
                    'locationto': ''})   
            rec.write({'locationfrom': [(5, 0, 0)],
                    'locationfrom': ''})   
            rec.write({'brandcategory': [(5, 0, 0)],
                    'brandcategory': ''})   
        vals = ({'none':None })   
        cinitial = self.get_cinitial(vals) 
        new_quotid =  self.env['ir.sequence'].get_per_doc_code(cinitial, 'QTEMP')   
        self.quotationitemid = new_quotid



                    
    def newdefault(self):  
        int_emp = self.getdefaultcustomerid()   
        return int_emp

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
            defcus = defaultcus.defaultcustomer.id ; str_a = str(record['customerid'].id)  
            if str(defcus) == str_a : record['iscorrectcust'] = True
            else                    : record['iscorrectcust'] = False

    def _value_search(self, operator, value):
        field_id = self.search([]).filtered(lambda x : x.iscorrectcust == value )
        return [('id', operator, [x.id for x in field_id] if field_id else False )]
            
    customerid = fields.Many2one('res.partner', string='CustomerID' , required=True, default=newdefault,   domain=[('is_logistic_customer','=',1)])   
    custinitial = fields.Char(string='Customer Initial' )          
    iscorrectcust = fields.Boolean(compute='_getcorrectcust',string="iscorrectcust", store=False,search='_value_search') 
    #coding customer id end  
    
    def cekdefaultfilter(self):  
        ir_filters = http.request.env['ir.filters'].sudo().search([('model_id','=','tl.tr.quotationitem')])
        ir_filters.sudo().unlink()
        self.env['ir.filters'].sudo().create({                                                               
            'name':'Group by customer & Location From',    'domain'  : '[]', 'context'   : "{'group_by': ['locationfrom']}",
            'sort': '[]',                       'model_id': 'tl.tr.quotationitem'           , 'is_default': 'True',            'active': 'True'     }  )
    #coding stage start
    
    def getdefaultstage(self): 
        result=[]
        str_a = 'x' 
        try:
            str_a = str(self.env.user.id)
        except ValueError:
            str_a = 'yyy' 
        get_companyinitial = """
        select b.modulename , a.orders, a.stage, a.stagedesc 
        from tl_ms_modulestage a 
        inner join tl_ms_modulelist b on a.modulename = b.id
        where b.modulename = 'tl_tr_draftwo' and a.stage = 'NEW' union all  
        select'Module Not Found' ,99,'NOTFOUND','Stage Not found, please check tl_ms_modulelist'  """
        #  where a.id = '"""+str(str_a)+"""' """ 
        self._cr.execute(get_companyinitial)
        cusinitial = ''
        # cusinitial = self._cr.fetchone()    
        cusinitial = self._cr.dictfetchall()
        try:
            result =  cusinitial[0]['stage']
        except ValueError:
            result= []
        return str(result)
         

    stage = fields.Selection(string="stage", selection=[("NEW",  "New stage"),("DRF",  "Draft"),("PUB",  "Published") ]) 
    
    #coding stage end
     

    @api.onchange('multitrip')
    def _onchange_multitrip(self):   
        vals = ({  'none'       :None })   
        cinitial = self.get_cinitial(vals)
        temporary_quotid =  self.env['ir.sequence'].get_per_doc_code(cinitial , 'QTEMP')  
           
        
        if(self.quotationitemid=='/'):
            self.quotationitemid = temporary_quotid 
            print(self.quotationitemid,'qii')

        firstloc = 0; lastloc = 0; rowcount = 0
        a = self.multitrip
        count = 0; ismulti = "NOTRIP"
        #ini jangan dirubah2 untuk nentuin lokasi from dan to nya [start]
        for id in a:
            count = count + 1 
            if(count == 1): firstloc = id._origin.id 
            lastloc = id._origin.id 
        #ini jangan dirubah2 untuk nentuin lokasi from dan to nya [end] 
        if(count > 10 ): ismulti = "OVERLOADTRIP"
        elif(count >2 ): ismulti = "MULTI"
        elif(count ==2): ismulti = "SINGLE"
        elif(count ==1): ismulti = "INCOMPLETE" #  >> bikin supaya user gak bisa pilih loc to kalo loc from blm diisi
        elif(count ==0): ismulti = "NOTRIP"

        self.ismultitrip =ismulti
        if(ismulti == "OVERLOADTRIP"): 
            raise ValidationError(ismulti)
        if(ismulti in("MULTI","SINGLE")):  
            table1=http.request.env['tl.tr.quotationitem.multitrip'].sudo().search([('id','=',firstloc)])  
            self.M2O_locationfrom = table1.locationfrom.id
            table1=table1.sudo().search([('id','=',lastloc)]) 
            self.M2O_locationto =  table1.locationfrom.id   
        if(ismulti == "INCOMPLETE"):  
            table1=http.request.env['tl.tr.quotationitem.multitrip'].sudo().search([('id','=',firstloc)]) 
            self.M2O_locationfrom = table1.locationfrom
            self.M2O_locationto = None   
        if(ismulti == "NOTRIP"):  
            self.M2O_locationfrom = None
            self.M2O_locationto = None 
   
            # self.M2O_locationfrom   = table1.locationfrom
            # self.M2O_locationto     = table2.locationfrom   
        return {'domain': {'multitrip': ['|',('quotationitemid','=',False), ('quotationitemid', '=', self.quotationitemid)]}}
     
         

                      
    def _reallocation(self): 
        for item in self: 
            item.locationfrom = item.M2O_locationfrom.locationname  
            item.locationto   = item.M2O_locationto.locationname 
        #ati2 benerin dsini. multitrip onchange bakal error
        # a= self.multitrip.quotationitemid
        # if(a):def
        #     for x in a:
        #         for y in x:
        #             print(y,'woooooooooooooooooooooooooooo')
    @api.onchange('M2O_locationfrom')
    def _onchange_M2O_locationfrom_validation(self):  
        self._reallocation() 
    @api.onchange('M2O_locationto')
    def _onchange_M2O_locationto_validation(self):  
        self._reallocation()

    salesprice               = fields.Float(    string='salesprice',                default =0, required=True)
    cost                     = fields.Float(    string='cost',                      default =0, required=True)    
    discount                 = fields.Float(    string='discount',                  default =0, required=True) 
    salespriceafterdiscount  = fields.Float(    string='salesprice after discount', default =0, required=True) 
    @api.onchange('discount')
    def _onchange_discount(self):   
        self.recalculate()
    @api.onchange('salesprice')
    def _onchange_salesprice(self):   
        self.recalculate()

    def recalculate(self): 
        self.salespriceafterdiscount = 0
        for record in self: 
            a = record['salesprice']
            b = record['discount']
            c = a-b
            record['salespriceafterdiscount'] = c

    #start setting brand
     
    M2O_brand       = fields.Many2one('tl.ms.productbrand', string="brand") 
    brandcategory   = fields.Char(string="category")
    brand           = fields.Char(string="brand")      
     
    @api.onchange('M2O_brand')
    def _onchange_M2O_brand_validation(self):    
        selfid = str(self.id)
        self.brandcategory = self.M2O_brand.category.category    
        # if('NewId_' not in selfid):    
        #     depend = self.env['tl.tr.quotationitem'].sudo().search([('id', '=', self.id)], limit=1)
        #     if(depend):
        #         depend.write({'brandcategory': self.M2O_brand.category.category})   

 
     
    wayoftransport  = fields.Selection( string="way of transport"   , required=True,   selection=[("TRUCKING",  "Trucking"),("SELFDRIVE",  "Self Drive"),("TOWING",  "Towing"),("CARRIER",  "Car Carrier") ]) 
    usingferries    = fields.Boolean(   string="use Ferries"        , default=False) 

    def name_get(self):
        result = []
        for s in self: 
            a= '	'
            while(len(a)<30):
                a= a+a 
            loc_dropA           = ''
            loc_from            =str('From:'  +s.M2O_locationfrom.locationname)
            if(s.pilihtrip=="MULTI" and s.dropA_M2O_location.locationname !=False): 
                loc_dropA       =str('Drop A:_['+s.dropA_M2O_location.locationname) +']' 
            loc_to              =str('To:'    +s.M2O_locationto.locationname)
            wayoftransport      =str(s.wayoftransport) ; ferries = ''; categ=''; brand=''; cusinit = ''; categbrand=''  
            if(s.wayoftransport =='TRUCKING'):  wayoftransport = '(✓)Trucking'
            if(s.wayoftransport =='SELF'    ):  wayoftransport = '(✓)Self Drive'
            if(s.wayoftransport =='TOW'     ):  wayoftransport = '(✓)Towing'
            if(s.wayoftransport =='CARRIER' ):  wayoftransport = '(✓)Car Carriage'
            
            wayoftransport =(str(wayoftransport)+ a)[0:15]   

            if(s.usingferries == True): ferries = '(✓)Ferries' 
            if(s.usingferries == True): ferries = '(✓)Ferries' 
            ferries =(ferries+ a)[0:11]   
            if(s.brandcategory  not in (False, None)): categ       =      (str(s.brandcategory)+ a)[0:5 ]    
            if(s.brand          not in (False, None)): brand       =      (str(s.brand        )+ a)[0:50]
            if(s.custinitial    not in (False, None)): cusinit     ='(Q:'+(str(s.custinitial  )+ a)[0:3 ]+')' 
            cusinit=''
            categbrand = '_[BRAND:CATEG]'.replace('CATEG',categ).replace('BRAND',brand)
            salesprice  =(str("Rp. {:,.0f}".format(s.salesprice) )+ a)[0:20]       
            
            name =   cusinit+'['+loc_from+']'+loc_dropA+'_['+loc_to+']_'+wayoftransport+'_'+ferries+categbrand+'_'+salesprice 
            name =   s.quotationitemid+' '+ name.replace('_',' ')
            result.append((s.id, name))
        return result 

    quotationitemid = fields.Char(default='/', string="Quotation item ID", readonly = True)  
    quotationid = fields.Char( string="Quotation ID", readonly = True)  
    msg = fields.Char( string="msg")  
      
    def getfromtolocation(self, multitrip): 
        tripct=0; firstloc=0; lastloc = 0 ; rowct = 0
        for row in multitrip:
            rowct = rowct + 1
            if(rowct == 1): 
                for id in row[2]:
                    tripct =tripct+1 ; table = self.env['tl.tr.quotationitem.multitrip'].search([('id', '=', id)], limit=1) 
                    if(tripct ==1 ):
                        firstloc =table.locationfrom.id
                        lastloc =table.locationfrom.id
                    if(tripct  >1 ):lastloc  =table.locationfrom.id   
             
        # if(rowct > 1):
        #     for id in row[2]: 
        #         table = self.env['tl.tr.quotationitem.multitrip'].search([('id', '=', id        )], limit=1)  ;lastloc = table.locationfrom.id    
        tbl_locationfrom  = self.env['tl.ms.customerlocation'       ].search([('id', '=', firstloc  )], limit=1) 
        tbl_locationto    = self.env['tl.ms.customerlocation'       ].search([('id', '=', lastloc   )], limit=1)  
        # print('firstloc:',tbl_locationfrom.locationname,'lastloc',tbl_locationto.locationname,'rowct:',rowct)
        
        idfrom            = tbl_locationfrom.id;   locationfrom    =tbl_locationfrom.locationname
        idto              = tbl_locationto.id  ;   locationto      =tbl_locationto.locationname 
        return idfrom, locationfrom, idto, locationto
        
    def get_cinitial(self, vals):
        result = vals.get('custinitial')
        if(result in(None,False)):
            defaultcus  = self.env['tl.ms.user'].search([('user_id', '=', self.env.user.id)], limit=1)  
            result = defaultcus.defaultcustomer.companyinitial   
        return result
        
    # def inserttomultitripquotationid(self, multitrip, quotationitemid):    
    #     for id in self.multitrip:
    #         y =self.env['tl.tr.quotationitem.multitrip'].sudo().search([('id', '=', id.id)])
    #         y.sudo().write({'quotationitem':self.id,'quotationitemid':self.quotationitemid}) 
    #     result = True

    #     return result
    # def benerinmultitripcaralama(self)
    #     multitrip = vals.get('multitrip')  ; dict ={}; data =[]; 
    #         if(vals.get('ismultitrip')=='MULTI'): 
    #             idfrom, locationfrom, idto, locationto = self.getfromtolocation(multitrip)
    #             vals['M2O_locationfrom']    = idfrom 
    #             vals['locationfrom']        = locationfrom
    #             vals['M2O_locationto']      = idto
    #             vals['locationto']          = locationto 
    #         validmultitrip = True    
    #         for row in multitrip:
    #             itemct = 0
    #             for item in row:
    #                 itemct = itemct + 1; sequence = 0
    #                 if(itemct==1 and item!=6)           : validmultitrip = False
    #                 if(itemct==2 and item!=False)       : validmultitrip = False
    #                 if(itemct==3 and item=='sequence')  : validmultitrip = False
    #                 if(itemct==3 and validmultitrip==True):   
    #                     for content in item:
    #                         sequence = sequence + 1
    #                         y = self.env['tl.tr.quotationitem.multitrip'].search([('id', '=', content)]) 
    #                         y.sudo().write({'sequence':sequence, 'sequenceview':sequence, 'quotationitem':this_id,'quotationitemid':new_quotationitemid})  

    def getitem_na(self):
        return self.env['tl.ms.loaditem'].search([('itemname', '=', 'n/a')], limit=1).id  
    @api.model
    def create(self, vals):   
        item_n_a = self.getitem_na()
        if('sgl_item_load_fr'       not in vals):vals['sgl_item_load_fr']     =item_n_a
        if('dropA_sgl_item_load'    not in vals):vals['dropA_sgl_item_load']  =item_n_a #baru
        if('sgl_item_load_to'       not in vals):vals['sgl_item_load_to']     =item_n_a
        if('sgl_item_unload_fr'     not in vals):vals['sgl_item_unload_fr']   =item_n_a
        if('dropA_sgl_item_unload'  not in vals):vals['dropA_sgl_item_unload']=item_n_a #baru
        if('sgl_item_unload_to'     not in vals):vals['sgl_item_unload_to']   =item_n_a 
        new_quotationitemid =  ''
        c_initial =  self.get_cinitial(vals) ; res =[] 
        new_quotationitemid = vals.get('quotationitemid') 
        if(new_quotationitemid in(None, False,'/')):
            new_quotationitemid = self.env['ir.sequence'].get_per_doc_code(c_initial, 'QT')  
        vals['quotationitemid'] = new_quotationitemid
        table_multitrip = self.env['tl.tr.quotationitem.multitrip']
        table_multitrip.search([('quotationitemid', '=', new_quotationitemid)]).sudo().unlink()  
        brand =  self.env['tl.ms.productbrand'].search([('id', '=', vals.get('M2O_brand'))], limit=1) 
        vals['brand']=  brand.manufacturer; vals['brandcategory']=  brand.category.category
        vals['custinitial'] =  c_initial ; vals['stage'] ="NEW"
        ##################### 
        multitrip =False; toggle_multitrip = "SINGLE"
        if(vals.get('pilihtrip')=="MULTI"): toggle_multitrip = "MULTI"  
        res = super(quotationitem, self).create(vals)  
        this_id = res.id 
        if(toggle_multitrip in ("SINGLE","MULTI")): 
            if(toggle_multitrip =="MULTI"):
                # self.benerinmultitripcaralama()
                table_multitrip.sudo().create({'sequence':1,'locationfrom'  :vals.get('M2O_locationfrom')  ,'loadtype':vals.get('sgl_loadtype_fr'   ),'item_load': vals.get('sgl_item_load_fr')   ,'item_unload':vals.get('sgl_item_unload_fr')   ,'sequenceview': 1,'quotationitem':this_id,'quotationitemid':new_quotationitemid,} )
                table_multitrip.sudo().create({'sequence':2,'locationfrom'  :vals.get('dropA_M2O_location'),'loadtype':vals.get('dropA_sgl_loadtype'),'item_load': vals.get('dropA_sgl_item_load'),'item_unload':vals.get('dropA_sgl_item_unload'),'sequenceview': 2,'quotationitem':this_id,'quotationitemid':new_quotationitemid,} )
                table_multitrip.sudo().create({'sequence':3,'locationfrom'  :vals.get('M2O_locationto')    ,'loadtype':vals.get('sgl_loadtype_to'   ),'item_load': vals.get('sgl_item_load_to')   ,'item_unload':vals.get('sgl_item_unload_to')   ,'sequenceview': 3,'quotationitem':this_id,'quotationitemid':new_quotationitemid,} )
            if(toggle_multitrip =="SINGLE"):
                table_multitrip.sudo().create({'sequence':1,'locationfrom' :vals.get('M2O_locationfrom'),'loadtype':vals.get('sgl_loadtype_fr'), 'item_load': vals.get('sgl_item_load_fr'),'item_unload':vals.get('sgl_item_unload_fr'), 'sequenceview': 1,'quotationitem':this_id,'quotationitemid':new_quotationitemid,} )
                table_multitrip.sudo().create({'sequence':2,'locationfrom' :vals.get('M2O_locationto')  ,'loadtype':vals.get('sgl_loadtype_to'), 'item_load': vals.get('sgl_item_load_to'),'item_unload':vals.get('sgl_item_unload_to'), 'sequenceview': 2,'quotationitem':this_id,'quotationitemid':new_quotationitemid,} )
            table_multitrip = table_multitrip.sudo().search([('quotationitemid', '=', new_quotationitemid)]) 
            data1 = []; cover = []; dtmultitrip = []
            for data in table_multitrip:
                dtmultitrip.append(data.id) 
            data1.append(6); data1.append(False); data1.append(dtmultitrip); cover.append(data1)  
            update_multi = self.env['tl.tr.quotationitem'].search([('id', '=',this_id )]) 
            length = len(cover[0][2])
            if (length <2):
                raise ValidationError('tl_tr_quotation_item1:apa yang sedang kamu lakukan itu akan membuat error system. silahkan input dari ulang.'); return
            elif (length ==False):
                raise ValidationError('tl_tr_quotation_item2:apa yang sedang kamu lakukan itu akan membuat error system. silahkan input dari ulang.'); return
            else:
                update_multi.sudo().write({'multitrip':cover, })  
        return res
    def hapustablelamadancreatebaru_defwrite(self, vals): 
        item_n_a = self.getitem_na() 
        table_multitrip = self.env['tl.tr.quotationitem.multitrip'].search([('quotationitemid', '=', self.quotationitemid)])
        table_multitrip.sudo().unlink()   
        multitrip =False; toggle_multitrip = "SINGLE"
        if(vals.get('pilihtrip')=="MULTI"): toggle_multitrip = "MULTI"   
        if(self.pilihtrip=="MULTI"): toggle_multitrip = "MULTI"   
        this_id = self.id 
        new_quotationitemid=self.quotationitemid
        data1 = []; cover = []; dtmultitrip = []  
        a_from      =vals.get('M2O_locationfrom'   ,self.M2O_locationfrom.id) 
        b_from      =vals.get('dropA_M2O_location' ,self.dropA_M2O_location.id)
        c_from      =vals.get('M2O_locationto'     ,self.M2O_locationto.id)
        a_loadtype  =vals.get('sgl_loadtype_fr'    ,self.sgl_loadtype_fr) 
        b_loadtype  =vals.get('dropA_sgl_loadtype' ,self.dropA_sgl_loadtype)
        c_loadtype  =vals.get('sgl_loadtype_to'    ,self.sgl_loadtype_to)
        
        a_itemload  =vals.get('sgl_item_load_fr'     ,self.sgl_item_load_fr.id) 
        b_itemload  =vals.get('dropA_sgl_item_load'  ,self.dropA_sgl_item_load.id)
        c_itemload  =vals.get('sgl_item_load_to'     ,self.sgl_item_load_to.id)
        a_itemunload=vals.get('sgl_item_unload_fr'   ,self.sgl_item_unload_fr.id) 
        b_itemunload=vals.get('dropA_sgl_item_unload',self.dropA_sgl_item_unload.id)
        c_itemunload=vals.get('sgl_item_unload_to'   ,self.sgl_item_unload_to.id)
        print('a_from      ',a_from      ) 
        print('b_from      ',b_from      )
        print('c_from      ',c_from      )
        print('a_loadtype  ',a_loadtype  )
        print('b_loadtype  ',b_loadtype  )
        print('c_loadtype  ',c_loadtype  ) 
        print('a_itemload  ',a_itemload  )
        print('b_itemload  ',b_itemload  )
        print('c_itemload  ',c_itemload  )
        print('a_itemunload',a_itemunload)
        print('b_itemunload',b_itemunload)
        print('c_itemunload',c_itemunload)
        # import ipdb; ipdb.set_trace()
        if(toggle_multitrip in ("SINGLE","MULTI")): 
            if(toggle_multitrip =="MULTI"): 
                table_multitrip.sudo().create({'sequence':1,'locationfrom'  :a_from,'loadtype':a_loadtype,'item_load': a_itemload,'item_unload':a_itemunload,'sequenceview': 1,'quotationitem':this_id,'quotationitemid':new_quotationitemid,} )
                table_multitrip.sudo().create({'sequence':2,'locationfrom'  :b_from,'loadtype':b_loadtype,'item_load': b_itemload,'item_unload':b_itemunload,'sequenceview': 2,'quotationitem':this_id,'quotationitemid':new_quotationitemid,} )
                table_multitrip.sudo().create({'sequence':3,'locationfrom'  :c_from,'loadtype':c_loadtype,'item_load': c_itemload,'item_unload':c_itemunload,'sequenceview': 3,'quotationitem':this_id,'quotationitemid':new_quotationitemid,} )
            if(toggle_multitrip =="SINGLE"):
                table_multitrip.sudo().create({'sequence':1,'locationfrom' :a_from,'loadtype':a_loadtype, 'item_load': a_itemload,'item_unload':a_itemunload, 'sequenceview': 1,'quotationitem':this_id,'quotationitemid':new_quotationitemid,} )
                table_multitrip.sudo().create({'sequence':2,'locationfrom' :c_from,'loadtype':c_loadtype, 'item_load': c_itemload,'item_unload':c_itemunload, 'sequenceview': 2,'quotationitem':this_id,'quotationitemid':new_quotationitemid,} )
            table_multitrip = table_multitrip.sudo().search([('quotationitemid', '=', new_quotationitemid)]) 
            for data in table_multitrip:
                dtmultitrip.append(data.id) 
            data1.append(6); data1.append(False); data1.append(dtmultitrip); cover.append(data1)   
            length = len(cover[0][2])
            if (length <2):
                raise ValidationError('tl_tr_quotation_item1xx:apa yang sedang kamu lakukan itu akan membuat error system. silahkan input dari ulang.'); return
            elif (length ==False):
                raise ValidationError('tl_tr_quotation_item2xx:apa yang sedang kamu lakukan itu akan membuat error system. silahkan input dari ulang.'); return
        return cover


    def write(self, vals):   
        cover = self.hapustablelamadancreatebaru_defwrite(vals) 
        vals['multitrip']=cover  
        if('M2O_brand' in vals):
            depend = self.env['tl.ms.productbrand'].sudo().search([('id', '=', vals.get('M2O_brand'))], limit=1) 
            categ = depend.category.category 
            vals['brandcategory'] = categ  
        res = super(quotationitem, self).write(vals)  
        return  res  
    
    def cekmultitripkosong(self,vals):
        bothid_ids = False
        multitrip =False; toggle_multitrip = "SINGLE"
        if(vals.get('pilihtrip')=="MULTI"): toggle_multitrip = "MULTI" 
        loadtype = 'BONGKARMUAT'
        if(self.jenistransaksi=='DU'): loadtype = 'DU'  
                
        if(toggle_multitrip=="SINGLE"): 
            if(loadtype == 'DU'): 
                self.env['tl.tr.quotationitem.multitrip'].search([('quotationitemid', '=', self.quotationitemid)]).sudo().unlink()
                from1   = self.M2O_locationfrom.id
                from2   = self.sgl_item_load_fr.id
                from3   = self.sgl_item_unload_fr.id
                to1     = self.M2O_locationto.id
                to2     = self.sgl_item_load_to.id
                to3     = self.sgl_item_unload_to.id
                print('before',self.M2O_locationfrom.locationname,'id',from1)
                print('before',self.M2O_locationto.locationname,'id',to1)

                valfrom1 = vals.get('M2O_locationfrom'  )
                valfrom2 = vals.get('sgl_item_load_fr'  )
                valfrom3 = vals.get('sgl_item_unload_fr')
                valto1   = vals.get('M2O_locationto'    )
                valto2   = vals.get('sgl_item_load_to'  )
                valto3   = vals.get('sgl_item_unload_to')

                if valfrom1 : from1  = valfrom1
                if valfrom2 : from2  = valfrom2
                if valfrom3 : from3  = valfrom3
                if valto1   : to1    = valto1
                if valto2   : to2    = valto2
                if valto3   : to3    = valto3   
                
                new_record1 = self.env['tl.tr.quotationitem.multitrip'].sudo().create({'sequence':1,'locationfrom' :from1,'loadtype':loadtype, 'item_load': from2,'item_unload':from3, 'sequenceview': 1,'quotationitem':self.id,'quotationitemid':self.quotationitemid,} )
                new_record2 = self.env['tl.tr.quotationitem.multitrip'].sudo().create({'sequence':2,'locationfrom' :to1  ,'loadtype':loadtype, 'item_load': to2  ,'item_unload':to3  , 'sequenceview': 2,'quotationitem':self.id,'quotationitemid':self.quotationitemid,} )
                bothid = self.env['tl.tr.quotationitem.multitrip'].sudo().search([('id', 'in', (new_record1.id, new_record2.id))]) 
                bothid_ids = [record.id for record in bothid] 
                # super(quotationitem, self).write({'multitrip': [(6, 0, bothid_ids)]})
            else:
                if(not self.multitrip): 
                    print('ga bisa di rubah lg.') 
                if(self.multitrip): 
                    print('masih bisa tapi belom ada codingan.') 

        else:
            raise ValidationError('tl_tr_quotation_item.py toggle_multitrip tidak dikenal')
        return bothid_ids
 

    multitrip           = fields.Many2many('tl.tr.quotationitem.multitrip', string="multi trip")
    
        #(0, 0,  { values })    link to a new record that needs to be created with the given values dictionary      