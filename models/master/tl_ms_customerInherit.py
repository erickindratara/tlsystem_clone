from ast import Store
from re import A
from traitlets import default
from odoo import api, fields, models, tools, _
  
class ResPartner(models.Model): 
    _inherit = 'res.partner'
     
  
    def cekdefaultfilter(self):  
        ir_filters = self.env['ir.filters'].sudo(); ir_filters.search([('model_id', '=', 'res.partner')]).sudo().unlink()  
        ir_filters.sudo().create({ 
            'model_id'  : 'res.partner' ,'name'        : "group by partner type"   ,
            'active'    : 'True'          ,'domain'    : '[]'  ,  
            'sort'      : "[]"            ,'context'   : "{'group_by': ['partnertype']}",
            'is_default': 'True',})
                 

    companyinitial = fields.Char(string='Company Initial',   placeholder="initial", style="color:#898687") #field di db  
    PIC = fields.Many2many('tl.ms.user', string="PIC users")  
 
    is_logistic_customer = fields.Boolean(string="is Logistic Customer")
 
    is_driver      = fields.Boolean(string="is driver")
    is_korlap      = fields.Boolean(string="is korlap")
    drivertype     = fields.Selection(string="Driver Tipe", selection=[("DRVFRE", "Driver Freelance"), ("DRVFIX", "Driver Fixed"),  ("OTHR", "Other") ])
    korlap         = fields.Many2one('res.partner', domain="[('is_korlap','=',True)]", string="Korlap")  #field di db
    driveralias    = fields.Char(string='driveralias') #field di db  
    partnertype = fields.Selection(string="partnertype",    selection=[("KORLAP"       , "Koordinator Lapangan"), 
                                                                            ("DRIVER"       , "Driver"              ), 
                                                                            ("KORLAPDRIVER" , "Korlap + Driver"     ), 
                                                                            ("LOGCUSTOMER"  , "Customer Logistic"   ), 
                                                                            ("OTHER"        , "Lain-Lain"           )]) 
    @api.onchange('partnertype', 'is_driver', 'is_korlap', 'drivertype','is_logistic_customer')
    def _compute_partnertype(self):
        for record in self:  
            partnertypeafter = self.getpartnertype(record.is_driver,record.is_korlap,record.is_logistic_customer)  
            if(self.partnertype!=partnertypeafter): 
                self.write({'partnertype': partnertypeafter})    

    def adjustpartnertype(self): 
        respartners = self.env['res.partner'].search([])
        for row in respartners:  
            partnertype = self.getpartnertype(row.is_driver,row.is_korlap,row.is_logistic_customer)
            if row.drivercategory in(None, False): row.sudo().write({'drivercategory': 'UMUM'})
            if row.partnertype != partnertype : row.sudo().write({'partnertype': partnertype})

    drivercategory = fields.Selection(string="drivercategory",   selection=[("DUSudeco"  , "Driver DU Sudeco"    ), 
                                                                            ("DUDaihatsu", "Driver DU Daihatsu"  ), 
                                                                            ("UMUM"      , "Driver Umum"         ), 
                                                                            ("DUUMUM"    , "Driver DU Umum"      ), 
                                                                            ("LOGUMUM"   , "Driver Logistic Umum")]) 
 
    def getpartnertype(self,is_driver,is_korlap,is_logistic_customer):
        partnertype = 'OTHER'  
        if (is_driver)                    :partnertype = 'DRIVER'
        if (is_korlap)                    :partnertype = 'KORLAP'
        if (is_korlap and is_driver)      :partnertype = 'KORLAPDRIVER'
        if (is_logistic_customer)         :partnertype = 'LOGCUSTOMER'  
        return partnertype
    
    def write(self, vals):      
        vals['partnertype']=self.createwrite_partnertype(vals)
        res = super(ResPartner, self).write(vals)  
        return res

    @api.model
    def create(self, vals):     
        vals['partnertype']=self.createwrite_partnertype(vals)
        res = super(ResPartner, self).create(vals) 
        return res 
    
    def createwrite_partnertype (self,vals):
        a=self.is_driver
        b=self.is_korlap
        c=self.is_logistic_customer 
        if 'is_driver'              in vals: a = vals.get('is_driver')  
        if 'is_korlap'              in vals: b = vals.get('is_korlap')
        if 'is_logistic_customer'   in vals: c = vals.get('is_logistic_customer') 
        partnertype = self.getpartnertype(a,b,c)
        return partnertype
    # PIC = fields.Many2many('tl.ms.user', 'tl_ms_customer_pic', string="PIC users")  

  