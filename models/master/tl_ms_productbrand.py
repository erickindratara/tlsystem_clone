from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models 
      

class productbrand(models.Model): #
    _name = 'tl.ms.productbrand' #nama di db berubah jadi training_course
    _description = 'Master productbrand'
    _rec_name = 'manufacturer'  

    def name_get(self):
        result = []
        for s in self:  
            name = s.manufacturer + ' / Category: '+str(s.category.category)  
            result.append((s.id, name))
        return result 

    #coding customer id start 
 
    @api.model
    def user_domain(self):    
        domain = [('is_logistic_customer','=',1)]    
        return domain 
 
    def getdefaultcustomerid(self): 
        str_a = 'x' 
        try:
            str_a = str(self.env.user.id)
        except ValueError:
            str_a = 'yyy' 
        get_employee = """ SELECT    distinct   b.defaultcustomer FROM   res_users a inner join tl_ms_user b on a.id = b.user_id   where a.id = '"""+str(str_a)+"""' """
        self._cr.execute(get_employee) 
        var_a = self._cr.dictfetchone()     
        defaultcustomer =var_a.get('defaultcustomer')   
        return int(defaultcustomer)

    def getdefaultcustinitial(self):         
        str_a = 'x' 
        try:
            str_a = str(self.env.user.id)
        except ValueError:
            str_a = 'yyy' 
        get_companyinitial = """ SELECT    distinct   b.companyinitial FROM   tl_ms_user a inner join res_partner b on a.defaultcustomer =b.id where a.user_id = '"""+str(str_a)+"""' """ 
        self._cr.execute(get_companyinitial)
        cusinitial = '' 
        var_a = self._cr.dictfetchone()     
        cusinitial =var_a.get('companyinitial')  
        return str(cusinitial)
 
    @api.model
    def defcust(self):   
        int_emp = self.getdefaultcustomerid() 
        str_emp = str(int_emp)  
        return str_emp  
    def newdefault(self):  
        int_emp = self.getdefaultcustomerid()
        selfdefault  = self.env['res.partner'].search([('id', '=', int_emp)], limit=1)    
        return selfdefault
        
    @api.model
    def _getcorrectcust(self):    
        for record in self: 
            defcus = str(record['defaultcustomer'])
            str_a = str(record['customerid'])
            # str_a = str(record['customerid'].get('id') )
            # str_a = str_a.replace(",", "")
            # str_a = str_a.replace("(", "")
            # str_a = str_a.replace(")", "")
            # str_a = str_a.replace("tl.ms.customer", "") 
            a = '?'
            while (len(a) < 100):
                a = a+a;  
            if str(defcus) == str_a : 
                record['iscorrectcust'] = True
            else:
                record['iscorrectcust'] = False
              
    def _value_search(self, operator, value):   
        field_id = self.search([]).filtered(lambda x : x.iscorrectcust == value )
        return [('id', operator, [x.id for x in field_id] if field_id else False )]
 
    @api.model
    def customer_domain(self):   
        int_emp=0
        try:
            int_emp = self.getdefaultcustomerid() 
        except ValueError:  
            int_emp=1
        domain = [('customerid','=',int_emp)]    
         
        return domain 

    def newdefault(self):  
        int_emp = self.getdefaultcustomerid()
        selfdefault  = self.env['res.partner'].search([('id', '=', int_emp)], limit=1)    
        return selfdefault
        
    customerid = fields.Many2one('res.partner', string='CustomerID' , default=newdefault,   domain=user_domain)   
    custinitial = fields.Char(default=getdefaultcustinitial, string='Customer Initial' , readonly=True)   
    defaultcustomer=fields.Integer(default=defcust, string ='defaultcustomer', store=False )       
    # iscorrectcust = fields.Boolean(string="iscorrectcust", store=False)
    iscorrectcust = fields.Boolean(compute='_getcorrectcust',string="iscorrectcust", store=False)
    # iscorrectcust = fields.Boolean(compute='_getcorrectcust',string="iscorrectcust", store=False,search='_value_search')

    #coding customer id end  
    
    # category =  fields.Many2one('tl.ms.productbrandcategory', string="category")  
    category =  fields.Many2one('tl.ms.productbrandcategory', string="category", domain=customer_domain)  
    catinitial = fields.Char(related="category.catinitial"        , string="catinitial", stored=True) 
    # brand       = fields.Char(string='brand', required=True) #field di db  
    manufacturer =fields.Selection(string="manufacturer"      , selection=[("TOYOTA", "Toyota"), ("DAIHATSU", "Daihatsu"),  ("SUZUKI", "Suzuki"),
                                                                           ("WULING", "Wuling"), ("BMW", "BMW"),  ("MERCEDES", "Mercedes-Benz"),
                                                                           ("FUSO", "Fuso"),("HINO","Hino"),("HONDA","Honda"),("ISUZU","ISUZU"),
                                                                           ("MITSUBISHI", "Mitsubishi"),("NISSAN","Nissan"),("DATSUN","Datsun") 
                                                                          ])
    
