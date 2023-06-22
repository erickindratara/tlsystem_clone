from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models 

class paymentallocation(models.Model): #
    _name = 'tl.tr.paymentallocation' #nama di db berubah jadi training_course
    _description = 'transaction payment allocation'
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
 

    paymentreceive = fields.Many2one('tl.tr.paymentreceive', string="paymentreceive") 
    allocationID = fields.Char(default='/', string ='allocationID', readonly = True)  
    # one2many get start

    wayofpayment = fields.Selection(related="paymentreceive.wayofpayment"        , string="wayofpayment")
    bankaccount =fields.Many2one(related="paymentreceive.bankaccount"        , string="bankaccount")
    bankaccountno =fields.Char(related="paymentreceive.bankaccountno"        , string="norek")
    
    bankbranch = fields.Char(related="paymentreceive.bankbranch"        , string="bankbranch")
    accountname = fields.Char(related="paymentreceive.accountname"        , string="accountname") 
    accountcode = fields.Char(related="paymentreceive.accountcode"        , string="accountcode")

    ba_initial =fields.Char(related="paymentreceive.ba_initial"        , string="ba_initial")

    bonmerahID =fields.Char(related="paymentreceive.bonmerahID"        , string="bonmerahID")
    additionalreferenceno = fields.Char(related="paymentreceive.additionalreferenceno"        , string="additionalreferenceno")
    source = fields.Selection(related="paymentreceive.source"                          , string="source")
    valuedate = fields.Datetime(related="paymentreceive.valuedate"                    , string="valuedate")
    amountreceive = fields.Float(related="paymentreceive.amountreceive"        , string="amountreceive")
    amountleft  = fields.Float(related="paymentreceive.amountleft"        , string="amountleft")
    description = fields.Char(related="paymentreceive.description", string="description")
    
    # one2many get end
    draftwo = fields.Many2one('tl.tr.draftwo',   string="draft wo", required=True)  
    #isi dari draftwo

    dwo_invoiceno           = fields.Char(related="draftwo.invoiceno",        string="invoice NO")
    dwo_stage               = fields.Selection(related="draftwo.stage",   string="stage")
    dwo_chassisno           = fields.Char(related="draftwo.chassisno",        string="No Rangka")
    dwo_engineno            = fields.Char(related="draftwo.engineno",        string="No Mesin")	
    dwo_agreement           = fields.Char(related="draftwo.engineno",        string="No Agrement")	
    dwo_senddate            = fields.Datetime(related="draftwo.senddate",        string="Tgl Kirim")
    dwo_manfactureyear      = fields.Char(related="draftwo.manfactureyear",        string="tahun dibuat")	
    dwo_color               = fields.Char(related="draftwo.color",        string="warna")
    # dwo_korlapid            = fields.Char(related="draftwo.korlapid",    string="Korlap")
    dwo_peopletype          = fields.Selection(related="draftwo.peopletype",   string="peopletype")
    dwo_driverid            = fields.Many2one(related="draftwo.driverid",    string="Driver")
    # dwo_quotationitem       = fields.Many2one(related="draftwo.quotationitem",    string="destination")
   
    dwo_quotationitemID     =fields.Char(related="draftwo.quotationitemID", string="quotationitemID")
    dwo_qi_brandcategory    =fields.Char(related="draftwo.qi_brandcategory", string="brandcategory") 
    dwo_qi_brand            =fields.Char(related="draftwo.qi_brand", string="brand")  
    dwo_qi_customerid       =fields.Char(related="draftwo.qi_customerid", string="customerid")
    dwo_qi_locationfrom     =fields.Char(related="draftwo.qi_locationfrom", string="locationfrom") 
    dwo_qi_locationto       =fields.Char(related="draftwo.qi_locationto", string="locationto")
    dwo_qi_salesprice       =fields.Float(related="draftwo.qi_salesprice", string="salesprice")
    dwo_qi_cost             =fields.Float(related="draftwo.qi_cost", string="cost")  

    # dwo_wono                = fields.Char(related="draftwo.wono",        string="WO NO")

    @api.model
    def create(self, vals):  
        c_initial=self.getdefaultcustinitial()  
        vals['allocationID'] = self.env['ir.sequence'].get_per_doc_code(c_initial, 'ALC')  
        return super(paymentallocation, self).create(vals)
