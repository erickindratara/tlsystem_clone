from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models 

class paymentreceive(models.Model): #
    _name = 'tl.tr.paymentreceive' #nama di db berubah jadi training_course
    _description = 'transaction payment receive'
    _rec_name = 'bonmerahID' 
    

    #coding customer id start
    @api.model
    def get_userid(self): 
        userid = self.env['tl.ms.user'].search([('user_id', '=', self._getresusers())], limit=1)  
        str_a = str(userid).replace('tl.ms.user(', '')
        str_a = str_a.replace(',)', '')  
        int_a = int(str_a)
        return int_a 
 
    @api.model
    def user_domain(self):   
        str_a = 'x' 
        try:
            str_a = self.get_userid()
        except ValueError:
            str_a = 99
        int_a = 1
        try:
            int_a = int(str_a)
        except ValueError:
            int_a = 1 
        domain = [('PIC','=',int_a)]    
        return domain 

    def _getresusers(self):   
        ctx = self.env.user  
        str_a = str(ctx)
        str_a = str_a.replace('res.users(', '')
        str_a = str_a.replace(',)', '')   
        try:
            int_a = int(str_a)  
        except ValueError:
            int_a = 'x123' 
        return int_a   
        
    def getdefaultcustomerid(self): 
        str_a = 'x' 
        try:
            str_a = str(self._getresusers())
        except ValueError:
            str_a = 'yyy' 
        get_employee = """ SELECT    distinct   b.defaultcustomer FROM   res_users a inner join tl_ms_user b on a.id = b.user_id   where a.id = '"""+str(str_a)+"""' """
        self._cr.execute(get_employee)
        employees = self._cr.fetchone()  
        employees = str(employees)  
        employees = str(employees).replace(",", "")  
        employees = str(employees).replace("(", "")  
        employees = str(employees).replace(")", "")  
        employees = str(employees).replace("'", "")  
        return int(employees)

    def getdefaultcustinitial(self):         
        str_a = 'x' 
        try:
            str_a = str(self._getresusers())
        except ValueError:
            str_a = 'yyy' 
        get_companyinitial = """ SELECT    distinct   c.companyinitial FROM   res_users a inner join tl_ms_user b on a.id = b.user_id   inner join tl_ms_customer c on c.id = b.defaultcustomer where a.id = '"""+str(str_a)+"""' """ 
        self._cr.execute(get_companyinitial)
        cusinitial = ''
        cusinitial = self._cr.fetchone()  
        cusinitial = str(cusinitial)  
        cusinitial = str(cusinitial).replace(",", "")  
        cusinitial = str(cusinitial).replace("(", "")  
        cusinitial = str(cusinitial).replace(")", "")  
        cusinitial = str(cusinitial).replace("'", "")  
        return str(cusinitial)
 
    @api.model
    def defcust(self):   
        int_emp = self.getdefaultcustomerid() 
        str_emp = str(int_emp)  
        return str_emp 
    @api.model
    def customer_domain(self):   
        int_emp = self.getdefaultcustomerid()
        domain = [('customerid','=',int_emp)]    
        return domain 
    def newdefault(self):  
        int_emp = self.getdefaultcustomerid()
        selfdefault  = self.env['tl.ms.customer'].search([('id', '=', int_emp)], limit=1)    
        return selfdefault

    @api.model
    def _getcorrectcust(self):   
        a = 0
        for record in self:
            a = a +1 
            defcus = str(record['defaultcustomer'])
            str_a = str(record['customerid'])
            str_a = str_a.replace(",", "")
            str_a = str_a.replace("(", "")
            str_a = str_a.replace(")", "")
            str_a = str_a.replace("tl.ms.customer", "") 
    
            if str(defcus) == str_a : 
                record['iscorrectcust'] = True
            else:
                record['iscorrectcust'] = False
              
    def _value_search(self, operator, value):
        field_id = self.search([]).filtered(lambda x : x.iscorrectcust == value )
        return [('id', operator, [x.id for x in field_id] if field_id else False )]

    customerid = fields.Many2one('tl.ms.customer', string='CustomerID' , default=newdefault,   domain=user_domain)  
    custinitial = fields.Char(default=getdefaultcustinitial, string='Customer Initial' , readonly=True)   
    defaultcustomer=fields.Integer(default=defcust, string ='defaultcustomer', store=False )     
    iscorrectcust = fields.Boolean(compute='_getcorrectcust',string="iscorrectcust", store=False,search='_value_search')
                                      
    #coding customer id end  
        #coding stage start
    def getdefaultstage(self): 
        result=[]
        str_a = 'x' 
        try:
            str_a = str(self._getresusers())
        except ValueError:
            str_a = 'yyy' 
        get_companyinitial = """
        select b.modulename , a.orders, a.stage, a.stagedesc 
        from tl_ms_modulestage a 
        inner join tl_ms_modulelist b on a.modulename = b.id
        where b.modulename = 'tl_tr_quotationitem' and a.stage = 'NEW' union all  
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

    # stage = fields.Char(default=getdefaultstage, string='stage' , readonly=True)   
    # stage = fields.Selection(string="stage", default=getdefaultstage, selection=[("NEW",  "New stage"),("Done",  "Done") ]) 
    stage = fields.Selection(string="stage", default=getdefaultstage, selection=[("NEW",  "New stage"),("PAR",  "Partially allocated"),("ALC",  "Fully Allocated"),("RVS",  "Reversed(reversal)") ]) 
    
    #coding stage end

    @api.onchange('bankaccount')
    def _onchange_quotationitem_validation(self):  
        self.ba_initial = self.bankaccount.pytreceivealias  
        self.bankaccountno = self.bankaccount.accountno  
        self.bankbranch = self.bankaccount.bankbranch  
        self.accountname = self.bankaccount.accountname  
        self.accountcode = self.bankaccount.accountcode  

    @api.onchange('amountreceive')
    def _onchange_amountreceive_validation(self):  
        self.amountleft = self.amountreceive

    wayofpayment = fields.Selection(default='BANK', string ='wayofpayment', selection=[("BANK", "Bank")], required=True)
    bankaccount = fields.Many2one('tl.ms.bankaccount', string="bankaccount", required=True) 
    bankaccountno = fields.Char(string="bankaccountno",readonly=True,  required=True) 
    bankbranch = fields.Char(string="bankbranch",readonly=True,  required=True) 
    accountname = fields.Char(string="accountname",readonly=True,  required=True) 
    accountcode = fields.Char(string="accountcode",readonly=True,  required=True) 
    ba_initial =fields.Char(string="initial", Store=True , readonly=True)

    bonmerahID = fields.Char(default='/', string ='referenceno', readonly = True)  
    additionalreferenceno = fields.Char(default='', string ='additionalreferenceno')  
    source = fields.Selection(default='PREPAID', string ='wayofpayment', selection=[("PREPAID", "Prepaid") ], required=True)   
    valuedate = fields.Datetime(string='valuedate',default='2022-01-01', required=True)
    amountreceive = fields.Float(string='amountreceive',default=5000000, required=True) 
    amountleft = fields.Float(string='amountleft',readonly=True, required=True) 
    description = fields.Char(default='', string ='description')  
    
    @api.model
    def create(self, vals):  
        c_initial=self.getdefaultcustinitial() 
        a = str(vals['ba_initial'])+'/'
        vals['bonmerahID'] = self.env['ir.sequence'].get_per_doc_code(c_initial, 'PAYR') 
        vals['bonmerahID'] = a+ vals['bonmerahID']
        return super(paymentreceive, self).create(vals)
