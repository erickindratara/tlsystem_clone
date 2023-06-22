from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models 
from odoo.exceptions import UserError, ValidationError


class invoice(models.Model): 
    
    _name = 'tl.tr.invoice' #nama di db berubah jadi training_course
    _description = 'Transaction invoice' 
    
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
        if(employees=='None'):
            employees = 0
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
        try:
            int_emp = self.getdefaultcustomerid() 
            selfdefault  = self.env['tl.ms.customer'].search([('id', '=', int_emp)], limit=1)    
        except ValueError:  
            selfdefault  = 'default customerid = newdefault, not found'
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
       

    invoiceno = fields.Char(default='/', string ='invoice no', readonly = True)   
    draftwono = fields.Many2many('tl.tr.draftwo', string="detail counts", domain=customer_domain) 
    
    @api.onchange('draftwono')
    def _onchange_draftwono_validation(self):  
        # self.quotationitemid.quotationid =self.quotationid 
        
        for record in self: 
            a = str(record['draftwono'])  
        # self.quotationitemid.quotationid ='x'
        # refreshdata = """
        #     update tl_tr_quotationitem set quotationid = """+a+""" where quotationitemid in ()
        # """
        # self._cr.execute(refreshdata) 
    
  
    @api.model
    def create(self, vals):   
        c_initial=self.getdefaultcustinitial() 
        vals['invoiceno'] = self.env['ir.sequence'].get_short_master(c_initial, 'INV')  
        invoiceno = vals['invoiceno']     
        res = super(invoice, self).create(vals) 
        # self.updateinvoiceno(invoiceno)
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
        where b.modulename = 'tl_tr_invoice' and a.stage = 'NEW' union all  
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
        
    stage = fields.Selection(string="stage", default=getdefaultstage, 
    selection=[("NEW",  "New stage"),
                ("SNT",  "Sent to Cust"),
                ("RCV",  "Received by Cust"),
                ("PAR",  "Partially paid") ,
                ("FUL",  "Full paid") 
                ]) 
    
 
    def action_confirmsent(self):
        invoiceno = self.invoiceno 
        self.stage ='SNT'
        self.updateitemstatus('SNT',invoiceno)
    def action_confirmreceived(self):
        invoiceno = self.invoiceno 
        self.stage ='RCV' 
        self.updateitemstatus('RCV',invoiceno)

    @api.model
    def updateitemstatus(self, stage, invoiceno):
        sqlstring = """
                update tl_tr_draftwo set stage =  '"""+stage+"""' where invoiceno = '"""+invoiceno+"""'; 
                """ 
        self._cr.execute(sqlstring) 

    @api.model
    def updateinvoiceno(self, invoiceno):
        sqlstring = """
                update tl_tr_draftwo set invoiceno = NULL where invoiceno = '"""+invoiceno+"""';
                update tl_tr_draftwo  
                set invoiceno  = '"""+invoiceno+"""'
                where dwoid  in (
                select c.dwoid  
                from tl_tr_draftwo_tl_tr_invoice_rel a 
                inner join tl_tr_invoice  b on a.tl_tr_invoice_id  = b.id
                inner join tl_tr_draftwo c on a.tl_tr_draftwo_id = c.id
                where b.invoiceno  =  '"""+invoiceno+"""'
                )
                """
        self._cr.execute(sqlstring) 

    @api.model
    def deleteinvoiceno(self, quotid):
        sqlstring = """
                update tl_tr_draftwo  
                set invoiceno  = NULL
                where dwoid  in (
                select c.dwoid  
                from tl_tr_draftwo_tl_tr_invoice_rel a 
                inner join tl_tr_invoice  b on a.tl_tr_invoice_id  = b.id
                inner join tl_tr_draftwo  c on a.tl_tr_draftwo_id = c.id
                where b.invoiceno  =  '"""+quotid+"""'
                )
                """
        self._cr.execute(sqlstring) 
    
 
    def write(self, vals):  
        invoiceno = str(self.invoiceno)    
        res = super(invoice, self).write(vals)
        #DISINI BUAT  CODE IF M2M ADDED THEN. IF M2M REDUCED THEN
        self.updateinvoiceno(invoiceno)        
        return res 

    def unlink(self):  
        invoiceno = str(self.invoiceno)    
        self.deleteinvoiceno(invoiceno)        
        res= super(invoice, self).unlink()
        return res
        

    def print_invoice(self): 
        datas = {
            'id': self.id, 
            'model': 'tl.tr.invoice',
            'data': 'data' [0],
        }   
        return self.env.ref('tlsystem.print_invoice').report_action(self, data=datas) 
 

class PrintInvoicePdf(models.AbstractModel): 
    _name = 'report.tlsystem.print_invoice_list'
    _description = 'Transaction invoice Print'
    @api.model
    def _get_report_values(self, docids, data=None): 
        
        datas = {
            'id': self.id, 
            'model': 'tl.tr.invoice',
            'data': 'data' [0],
        }  
        # invoice_obj = self.env['tl.tr.invoice'].sudo().search([('id','=',data['id'])])  
        invoice_obj = self.env['tl.tr.invoice'].sudo().search([('id','=',datas['id'])])   
        return {
            'docs': datas['data'],
            'people_obj': invoice_obj,
            'date': fields.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        