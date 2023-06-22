from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models, _  
from odoo.exceptions import UserError, ValidationError
#  _inherit = "dms.sub.location"

class customerlocation(models.Model): #
    _name = 'tl.ms.customerlocation' #nama di db berubah jadi training_course
    _description = 'Master Customer Location'
    _rec_name = 'locationname' 
    ref = fields.Char(default='/', string ='ref', readonly = True) 
    
    locationname = fields.Char(string='Location Name', required=True) #field di db  
     

    firstletter = fields.Selection(string="FirsLetter", selection=[  ("A", "A"), 
                                                                ("B", "B"),
                                                                ("C", "C"),
                                                                ("D", "D"),
                                                                ("E", "E"),
                                                                ("F", "F"),
                                                                ("G", "G"),
                                                                ("H", "H"),
                                                                ("I", "I"),
                                                                ("J", "J"),
                                                                ("K", "K"),
                                                                ("L", "L"),
                                                                ("M", "M"),
                                                                ("N", "N"),
                                                                ("O", "O"),
                                                                ("P", "P"),
                                                                ("Q", "Q"),
                                                                ("R", "R"),
                                                                ("S", "S"),
                                                                ("T", "T"),
                                                                ("U", "U"),
                                                                ("V", "V"),
                                                                ("W", "W"),
                                                                ("X", "X"),
                                                                ("Y", "Y"),
                                                                ("Z", "Z") ])  
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
        selfdefault  = self.env['res.partner'].search([('id', '=', 43)], limit=1)    
        return selfdefault

    customerid = fields.Many2one('res.partner', string='CustomerID' , default=newdefault,   domain=user_domain)   
    # custinitial = fields.Char(default=getdefaultcustinitial, string='Customer Initial' , readonly=True)   
    custinitial = fields.Char(string="Customer Initial")#store=True
    defaultcustomer=fields.Integer(default=defcust, string ='defaultcustomer', store=False )        
    iscorrectcust = fields.Boolean(compute='_getcorrectcust',string="iscorrectcust", store=False)
    # iscorrectcust = fields.Boolean(compute='_getcorrectcust',string="iscorrectcust", store=False,search='_value_search')

    @api.onchange('customerid')
    def cus_onchange(self):  
        self.custinitial = self.customerid.companyinitial


    def messageshow(self):
         raise ValidationError(self)
    #coding customer id end 
    


        
    @api.model
    def create(self, vals):   
        c_initial =''    
        if 'custinitial' in vals:
            c_initial = str(vals['custinitial']) 
            vals['ref'] = self.env['ir.sequence'].get_per_doc_code(c_initial, 'CL')  
            res = super(customerlocation, self).create(vals)
            return res 
    

 