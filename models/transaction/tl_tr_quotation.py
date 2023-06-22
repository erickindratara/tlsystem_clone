from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models 
from odoo.exceptions import UserError, ValidationError


class quotation(models.Model): 
    
    _name = 'tl.tr.quotation' #nama di db berubah jadi training_course
    _description = 'Transaction quotation' 
    
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
        domain = [('is_logistic_customer','=',1)]    
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

    @api.model
    def _getcorrectcust(self):    
        for record in self: 
            defcus = str(record['defaultcustomer'])
            str_a = str(record['customerid'].id)  
            if str(defcus) == str_a : 
                record['iscorrectcust'] = True
            else:
                record['iscorrectcust'] = False

    def _value_search(self, operator, value):
        field_id = self.search([]).filtered(lambda x : x.iscorrectcust == value )
        return [('id', operator, [x.id for x in field_id] if field_id else False )]
        
    
    customerid = fields.Many2one('res.partner', string='CustomerID' , default=newdefault,   domain=user_domain)   
    custinitial = fields.Char(default=getdefaultcustinitial, string='Customer Initial' , readonly=True)   
    defaultcustomer=fields.Integer(default=defcust, string ='defaultcustomer', store=False )        
    iscorrectcust = fields.Boolean(compute='_getcorrectcust',string="iscorrectcust", store=False,search='_value_search') 
    #coding customer id end  
       

    quotationid = fields.Char(default='/', string ='Quotation ID', readonly = True)   
    quotationitemid = fields.Many2many('tl.tr.quotationitem', string="detail counts") 
    # quotationitemid = fields.Many2many('tl.tr.quotationitem', string="detail counts", domain=customer_domain) 
    
    @api.onchange('quotationitemid')
    def _onchange_quotationitemid_validation(self):  
        # self.quotationitemid.quotationid =self.quotationid 
        
        for record in self: 
            a = str(record['quotationitemid'])  
        # self.quotationitemid.quotationid ='x'
        # refreshdata = """
        #     update tl_tr_quotationitem set quotationid = """+a+""" where quotationitemid in ()
        # """
        # self._cr.execute(refreshdata) 
        
 

    debug = fields.Char(string="debug", default=customer_domain) 
  
    @api.model
    def create(self, vals):   
        c_initial=self.getdefaultcustinitial() 
        vals['quotationid'] = self.env['ir.sequence'].get_short_master(c_initial, 'Q')  
        quotid = vals['quotationid']     
        res = super(quotation, self).create(vals)
        # self._cr.execute(refreshdata) 
        self.updatequotid(quotid)
        return res
 
    @api.model
    def getdefaultstage(self): 
        result=[]
        str_a = 'x' 
        try:
            str_a = str(self._getresusers())
        except ValueError:
            str_a = 'yyy' 
        sqlstring = """
        select b.modulename , a.orders, a.stage, a.stagedesc 
        from tl_ms_modulestage a 
        inner join tl_ms_modulelist b on a.modulename = b.id
        where b.modulename = 'tl_tr_quotation' and a.stage = 'NEW' union all  
        select'Module Not Found' ,99,'NOTFOUND','Stage Not found, please check tl_ms_modulelist'  """
        #  where a.id = '"""+str(str_a)+"""' """ 
        self._cr.execute(sqlstring)
        cusinitial = ''
        # cusinitial = self._cr.fetchone()    
        cusinitial = self._cr.dictfetchall()
        try:
            result =  cusinitial[0]['stage']
        except ValueError:
            result= []
        return str(result)
        
    stage = fields.Selection(string="stage", default=getdefaultstage, selection=[("NEW",  "New stage"),("DRF",  "Draft"),("PUB",  "Published") ]) 
    
 
    def action_confirmposting(self):
        quotid = self.quotationid 
        self.stage ='PUB'
        self.updateitemstatus('PUB',quotid)
    def action_confirmrevertdraft(self):
        quotid = self.quotationid 
        self.stage ='DRF' 
        self.updateitemstatus('DRF',quotid)

    @api.model
    def updateitemstatus(self, stage, quotid):
        sqlstring = """
                update tl_tr_quotationitem set stage =  '"""+stage+"""' where quotationid = '"""+quotid+"""'; 
                """
        self._cr.execute(sqlstring) 

    @api.model
    def updatequotid(self, quotid):
        refreshdata = """
                update tl_tr_quotationitem set quotationid = NULL where quotationid = '"""+quotid+"""';
                update tl_tr_quotationitem  
                set quotationid  = '"""+quotid+"""'
                where quotationitemid  in (
                select c.quotationitemid  
                from tl_tr_quotation_tl_tr_quotationitem_rel a 
                inner join tl_tr_quotation  b on a.tl_tr_quotation_id  = b.id
                inner join tl_tr_quotationitem c on a.tl_tr_quotationitem_id = c.id
                where b.quotationid  =  '"""+quotid+"""'
                )
                """
        self._cr.execute(refreshdata) 

    @api.model
    def deletequotid(self, quotid):
        refreshdata = """
                update tl_tr_quotationitem  
                set quotationid  = NULL
                where quotationitemid  in (
                select c.quotationitemid  
                from tl_tr_quotation_tl_tr_quotationitem_rel a 
                inner join tl_tr_quotation  b on a.tl_tr_quotation_id  = b.id
                inner join tl_tr_quotationitem c on a.tl_tr_quotationitem_id = c.id
                where b.quotationid  =  '"""+quotid+"""'
                )
                """
        self._cr.execute(refreshdata) 
    
 
    
    def write(self, vals):  
        quotid = str(self.quotationid)    
        res = super(quotation, self).write(vals)
        #DISINI BUAT  CODE IF M2M ADDED THEN. IF M2M REDUCED THEN
        self.updatequotid(quotid)        
        return res 

    def unlink(self): 
        quotid = str(self.quotationid)    
        self.deletequotid(quotid)        
        res= super(quotation, self).unlink()
        return res