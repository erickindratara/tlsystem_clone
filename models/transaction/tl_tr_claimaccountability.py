from ast                import Store
from cgitb              import text
from ctypes             import create_unicode_buffer
from dataclasses        import replace
from email.policy       import default
from http.client        import FOUND
from operator           import truediv
from tracemalloc        import DomainFilter
from typing_extensions  import Required
from venv               import create
from weakref            import ref
from odoo               import api, fields, models, _
from odoo.exceptions    import UserError, ValidationError
from datetime           import date, timedelta 
try:
    import simplejson as json
except ImportError:
    import json
  
class claimaccountabilityapproval(models.Model): #
    _name           = 'tl.tr.claimaccountabilityapproval' #nama di db berubah jadi training_course
    _description    = 'approval uang jalan'   
    parent_id       = fields.Integer(string='parent_id', default='' )  
    sequence        = fields.Integer(string='seq', default='' )    
    userapproval    = fields.Many2one('tl.ms.userapproval')    
    approvallevel   = fields.Char(string='Approval level' )   
    approvaldate    = fields.Datetime(string='Action Date') 
    approvalnote    = fields.Text(string='approvalnote', default='' )    
    claimid         = fields.Text(string='ClaimID', default='' )    
     

    def unlink(self):     
        res = super(claimaccountabilityapproval, self).unlink()  
        return res   
    
    def write(self, vals):    
        res = super(claimaccountabilityapproval, self).write(vals)  
        return res   
    
    @api.model
    def create(self, vals):      
        res     = super(claimaccountabilityapproval, self).create(vals) 
        return res 
class claimaccountability(models.Model): 
    _name           = 'tl.tr.claimaccountability'  
    _description    = 'Uang Jalan Transaction'  
    _rec_name       = 'claimid'   
    claimid         = fields.Char(string='ClaimID', default='/' )    
    counts          = fields.Integer(compute='_compute_counts', string='WO Count'   ,store=False)
    sumcost         = fields.Integer(compute='_compute_counts', string='Total Cost' ,store=False)
    sumclaim        = fields.Integer(compute='_compute_counts', string='Total Uang Jalan',store=False)
    sumclaim        = fields.Integer(compute='_compute_counts', string='Total Uang Jalan',store=False)
    approval        = fields.Many2many('tl.tr.claimaccountabilityapproval')  
    korlap_id       = fields.Many2one('res.partner', string='Korlap' , required=True,  domain=[('is_korlap','=',1)])    
    currentapprover = fields.Boolean(compute='_iscurrentapprover',string="iscorrectcust", store=False)  
      
    @api.model
    def _iscurrentapprover(self):     
        for record in self:  
            print('anjing',record['currentapprover'])
            iscurrentapprover = False  
            order = 0
            currstage = record.stage  
            if(currstage =="DIC"        ):order = 1
            if(currstage =="REQ-C/OP1"  ):order = 2
            if(currstage =="REQ-C/OP2"  ):order = 3
            if(currstage =="REQ-C/FN1"  ):order = 4
            if(currstage =="REQ-C/FN2"  ):order = 5
            if(currstage =="CLAIMPAID"  ):order = 6
            curruser= self.env['tl.ms.userapproval'].search([('model.model' ,'=', 'tl.tr.claimaccountability'),
                                                             ('user_id'     ,'=', self.env.user.id),
                                                             ('order'       ,'=', order),
                                                             ], limit=1)   
            for id in curruser:
                if(id.id): iscurrentapprover = True   
            record['currentapprover'] = iscurrentapprover 
        

    @api.depends('draftwo')
    def _compute_counts(self):         
        for record in self: 
            record.counts   =  len(record.draftwo)  
            record.sumcost  =  sum(record.draftwo.mapped('qi_cost'))
            record.sumclaim =  sum(record.draftwo.mapped('claimamount'))   
    @api.onchange('draftwo')
    def onchange_draftwo(self):         
        wokorlap = False
        for record in self: 
            wokorlap =record.draftwo.korlap_id
            if(wokorlap not in (False,None)):
                break
        
        if(wokorlap not in (False,None)):
            self.korlap_id = wokorlap 
            
  
    def cekdefaultfilter(self):  
        ir_filters = self.env['ir.filters'].sudo(); ir_filters.search([('model_id', '=', 'tl.tr.claimaccountability')]).sudo().unlink()  
        ir_filters.sudo().create({ 
            'model_id'  : 'tl.tr.claimaccountability'   ,'name'      : "stage in New, Draft. Group by Send Date"   ,
            'active'    : 'True'                        ,'domain'    : '[]'  , 
            'sort'      : "[]"            ,'context'   : "{'group_by': ['stage','customerid',]}",
            'is_default': 'True',})
                 
    #coding customer id start 
 
    @api.onchange('customerid')
    def cus_onchange(self):    
        cinitial  = self.env['tl.ms.user'].search([('user_id', '=', self.env.user.id)], limit=1)  
        cinitial = cinitial.defaultcustomer.companyinitial  
        if(self.customerid!=None and self.customerid.id != False): 
            cinitial = self.customerid.companyinitial ; self.custinitial = cinitial
            self._cr.execute( """ update tl_ms_user set defaultcustomer =  '"""+str(self.customerid.id)+"""'  where user_id = '"""+str(self.env.user.id)+"""' """)
        
            
            tblcustomer  = self.env['res.partner'].search([('id', '=', self.customerid.id)], limit=1)     
            self._cr.execute( """ update tl_ms_user set defaultcustomer =  '"""+str(self.customerid.id)+"""'  where user_id = '"""+str(self.env.user.id)+"""' """)
        return {'domain': {'draftwo': ['&',('wono', '!=', False),('stage', '=', 'RTC'),('customerid', '=', self.customerid.id)]}}
   

  
    def newdefault(self):  
        int_emp = self.getdefaultcustomerid()   
        return int_emp

    customerid = fields.Many2one('res.partner', string='Customer Name' , required=True, default=newdefault,   domain=[('is_logistic_customer','=',1)])   
 
 
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
    #coding customer id end  
     

    claimaccountabilitydate =fields.Datetime(string='Tanggal Uang Jalan', required=True, default=fields.Datetime.now)

    draftwo = fields.Many2many('tl.tr.draftwo',  required=True)  
        
  
    stage = fields.Selection(string="stage", default="NEW", 
            selection=[ ("NEW",                      "Newly Created"),
                        ("DIC",                "Draft In Uang Jalan"),    
                        ("REQ-C/OP1",   "Req App Uang Jalan OPS SPV"),
                        ("APV-C/OP1",             "OPS SPV Approved"),
                        ("REQ-C/OP2",   "Req App Uang Jalan OPS MGR"), 
                        ("APV-C/OP2",             "OPS MGR Approved"),
                        ("REQ-C/FN1",   "Req App Uang Jalan FNC SPV"),
                        ("APV-C/FN1",             "FNC SPV Approved"), 
                        ("REQ-C/FN2",   "Req App Uang Jalan FNC MGR"),
                        ("APV-C/FN2",             "FNC MGR Approved"),  
                        ("APV-C/COM","Approval Uang Jalan Completed"),   
                        ("CLAIMPAID",     "Uang Jalan Has Been Paid"),    
                        ("PLOTREQ"   ,                        "Need Driver Allocation"),    #100
                        ("PLOTTED"   ,                       "Driver has been plotted"),    #200
                        ("MBL/DRVACC",                         "Driver Accepted Order"),    #400
                        ("MBL/DRVOTW",                "Driver is On the way(to Loc A)"),    #700
                        ("MBL/DRVLCA",                          "Driver on Location A"),    #800
                        ("MBL/DRVIPU",                                "Item Picked Up"),    #810
                        ("MBL/DRVLCB",                    "Item Dropped on Location B"),    #800
                        ("MBL/DRVDNE",                                    "Order Done"),    #900
                        ("DRVPJDONE" ,     "Driver telah pertanggungjawaban ke korlap"),    #new  
                        ("RTP"      ,     "Ready To create Pertanggung Jawaban"),    
                        ("CIC",                  "Canceled/Rejected")
                        ])  
    
      
    @api.onchange('claimaccountabilitydate','invostageiceno')
    def all_onchange(self):  
        if(self.stage=='NEW'):
            self.stage ='DIC' 
  


    def defcreate_validasicustomer(self, vals): 
        draftwo = vals.get('draftwo'); iterable_draftwo = False; item_index = 0; msg = False; result = True
        for cover in draftwo:
            for column in cover:  
                item_index = item_index+1
                try: iter(column)
                except TypeError: print(column,"Object not an iterable")
                else: 
                    if(item_index==3): iterable_draftwo = column 
        if(len(list(iterable_draftwo)) ==0):
            raise ValidationError('draftwo tidak ditemukan, jangan di save dulu, harus ada isinya')   
        if(iterable_draftwo == False):
            raise ValidationError('draftwo tidak ditemukan, iterable_draftwo =False')   
        for id in iterable_draftwo: 
            tbldwo = self.env['tl.tr.draftwo'].sudo().search([('id','=',id)])     
            hdcust = vals.get('customerid'); dtcust = tbldwo.customerid.id
            hdcustname = self.env['tl.tr.draftwo'].sudo().search([('id','=',hdcust)]).customerid.name    
            dtcustname = tbldwo.customerid.name 
            if(hdcust !=dtcust):msg = 'anda sedang memilih customer: ['+str(hdcustname)+'], silahkan  pilihdraft wo yang sesuai. karena nomor:#DWO# adalah transaksi milik customer:['+str(dtcustname)+'], silahkan di revisi datanya'
            elif(tbldwo.stage       not in ('RTC'       )): msg = 'ax stage [#DWO#]-['+str(tbldwo.stage)+'] yang anda  pilih berada diluar stage yang boleh dipakai untuk membuat claim. hanya boleh di [RTC- Ready to Claim]. silahkan revisi data yang anda pilih'
            elif(tbldwo.activestage not in ('ACT'       )): msg = 'z activestage [#DWO#]-['+str(tbldwo.activestage)+'] yang anda  pilih berada diluar activestage yang boleh dipakai untuk membuat claim. hanya boleh di [ACT]. silahkan revisi data yang anda pilih'
            elif(tbldwo.invoiceno   !=          False    ): msg = 'y nomor [#DWO#] sudah berada dalam invoice ['+str(tbldwo.invoiceno)+'] tidak bisa dibuatkan claim  lagi.'
            elif(tbldwo.claimid     !=          False    ): msg = 'x nomor [#DWO#] sudah berada dalam claim ['+str(tbldwo.claimid)+'] tidak bisa dibuatkan claim  lagi.'
            if(msg != False):
                result = False; msg= msg.replace('#DWO#',tbldwo.dwoid)
                raise ValidationError(msg)     

    @api.model
    def create(self, vals):   
        self.defcreate_validasicustomer(vals) 
        c_initial =  vals.get('custinitial')
        if(c_initial in (None, False)):
            c_initial = self.env['tl.ms.user'].search([('user_id', '=', self.env.user.id)], limit=1).defaultcustomer.companyinitial   
            vals['custinitial'] =c_initial 
        claimid = self.env['ir.sequence'].get_short_master(c_initial, 'CLAIM'); vals['claimid'] =claimid  ; vals['stage'] ='DIC'   
        res     = super(claimaccountability, self).create(vals)
        self.defcreate_updatewono(vals) 
        return res
    def defwrite_getitemremoved(self, vals):
        id_list=False; removed=False
        dwo = vals.get('draftwo') 
        if(self.draftwo):
            id_list = [obj.id for obj in self.draftwo]
        if(dwo):
            dwo = (dwo[0][2])
        if(id_list and dwo):
            print('vals:',dwo,'self:',id_list   )
            removed = [num for num in id_list if num not in dwo] 
        return removed

    def write(self, vals):  
        removed=self.defwrite_getitemremoved(vals) 
        self.defwrite_validasicustomer(vals)  
        res = super(claimaccountability, self).write(vals) 
        self.defwrite_updatewono(vals) 
 
    def defwrite_validasicustomer(self, vals):
        draftwo = vals.get('draftwo')  
        if draftwo: 
            for dw in draftwo:
                if(dw[0]==6):
                    dw_id = dw[2] 
                    dew_id = False
                    for id in dw_id:
                        try: 
                            dew_id = int(id) 
                        except ValueError: 
                            continue
                    currentclaimid = vals.get('claimid') or self.claimid 
                    dw_record   = self.env['tl.tr.draftwo'].search([('id', '=', dew_id)]); hdcust = vals.get('customerid'); msg =False
                    if not hdcust: hdcust = self.customerid.id 
                    hdcustname  = self.env['tl.tr.draftwo'].sudo().search([('customerid','=',hdcust)]).customerid.name; dtcustname = dw_record.customerid.name
                    if hdcust  != dw_record.customerid.id      : msg = 'anda sedaaang memilih customer: [{hdcustname}], silahkan pilih draft wo yang sesuai. karena nomor:{dwo_id} adalah transaksi milik customer:[{dtcustname}], silahkan di revisi datanya';msg = msg.format(hdcustname=hdcustname, dwo_id=dw_record.dwoid, dtcustname=dtcustname)
                    elif dw_record.stage  not in ('RTC','DIC',): msg = 'stage [{dwo_id}]-[{stage}] yang anda pilih berada diluar stage yang boleh dipakai untuk membuat/edit pengajuan uang jalan. hanya boleh di [RTC- Ready to Claim]. silahkan revisi data yang anda pilih'; msg = msg.format(dwo_id=dw_record.dwoid, stage=dw_record.stage) 
                    elif dw_record.activestage  not in ('ACT',): msg = 'activestage [{dwo_id}]-[{activestage}] yang anda pilih berada diluar activestage yang boleh dipakai untuk membuat claim. hanya boleh di [ACT]. silahkan revisi data yang anda pilih';msg = msg.format(dwo_id=dw_record.dwoid, activestage=dw_record.activestage) 
                    elif dw_record.invoiceno                   : msg = 'nomor [{dwo_id}] sudah berada dalam {type} [{num}] tidak bisa dibuatkan claim lagi.'; msg = msg.format(dwo_id=dw_record.dwoid, type='invoice', num=dw_record.invoiceno) 
                    elif dw_record.claimid != currentclaimid   : msg = 'nomor [{dwo_id}] sudah berada dalam {type} [{num}] tidak bisa dibuatkan claim lagi.'; msg = msg.format(dwo_id=dw_record.dwoid, type='claim'  , num=dw_record.claimid) 
                    if(msg!=False):
                        raise ValidationError(msg) 
                # import ipdb; ipdb.set_trace()
            
    @api.model
    def defwrite_updatewono(self, vals):      
        for s in self:
            vdwo= s.draftwo;  claimid=s.claimid  ; korlap_id=s.korlap_id
            if(vdwo not in (None, False)): 
                for id in vdwo:   
                        draftwo = False 
                        draftwo =self.env['tl.tr.draftwo'].search([('id', '=', id.id)])     
                        if(draftwo!=False and draftwo.stage in ('RTC','DIC')):
                            if(draftwo.stage =='RTC'):
                                draftwo.sudo().write({'claimid':claimid,'stage':'DIC'}) 
                            if(draftwo.stage =='DIC'):
                                draftwo.sudo().write({'claimid':claimid, 'korlap_id':korlap_id}) 
                        else:
                            draftwo_korlap =self.env['tl.tr.draftwo'].search([('id', '=', id.id)])   
                            draftwo_korlap.sudo().write({'korlap_id':korlap_id}) 
                            
                       
 
         
    @api.model
    def defcreate_updatewono(self, vals):    
        vdwo= vals.get('draftwo'); wono= vals.get('woid'); claimid= vals.get('claimid'); korlap_id= vals.get('korlap_id') 
        if(vdwo not in (None, False)): 
            for id in vdwo:  
                list = (id[2])
                for idx in list:  
                    draftwo = False
                    a=0; e = 'EE'
                    try: idx = int(idx)
                    except Exception as e: 
                        print('skip')
                    else:  
                        draftwo =self.env['tl.tr.draftwo'].search([('id', '=', idx)])  
                        if(draftwo!=False):
                            draftwo.sudo().write({'claimid':claimid, 'korlap_id': korlap_id})  
 
    def unlink(self):          
        if (len(self) > 1): 
            raise ValidationError('Bulk delete is not allowed. Please delete records one by one.') 
        else:  
            for record_id in self: 
                claim_aa =  self.env['tl.tr.claimaccountability'].sudo().browse(record_id.id) 
                stage = claim_aa.stage  
                if stage in ('NEW', 'DIC','CIC','CIV'): 
                    if not claim_aa.draftwo:                        
                        oktodeletethis=True   
                    else:     
                        draftwo = self.env['tl.tr.draftwo'].sudo().search([('id', 'in', claim_aa.draftwo.ids)])
                        draftwo_list = draftwo.mapped('id') 
                        for row in draftwo: 
                            self.env['tl.tr.draftwo'].sudo().search([('id', '=', row.id)]).sudo().write({'stage': 'RTC','activestage': 'CIC','claimid': False,}) 
            claim_aa.sudo().write({'stage': 'CIC','draftwo': False,})   #it will clear the data first 
            res = super(claimaccountability, self).unlink()
            return res 
         
    @api.model 
    def button_sameascost(self, ids):
        for record_id in ids:
            record = self.browse(record_id)
            if(record.stage=='DIC'):
                for id in record.draftwo: 
                    tbl_dw = self.env['tl.tr.draftwo'].sudo().search([('id', '=', id.id)])
                    tbl_dw.sudo().update({'claimamount': tbl_dw.qi_cost})
            else:
                msg = "cannot update claimamount, only works in DIC (Draft In Claim) Stage."
                raise ValidationError(msg) 
  
    @api.model
    def btn_debughapusapproval(self, ids):
        message ='''it will send this approval to non existence, are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.claimaccountability','method': 'btn_debughapusapproval','record_id' : record.id,'message'   : message, 'requirenotes'   : False, })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 

    @api.model
    def btn_reqapprovalclaim(self, ids):
        message ='''it will send this to approval, are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.claimaccountability','method': 'btn_reqapprovalclaim','record_id' : record.id,'message'   : message, 'requirenotes'   : False,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    @api.model
    def btn_spvopsapprovalclaim(self, ids): 
        message ='''it will approve this claim request and send this to OPS MGR approval, are you sure?''' 
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.claimaccountability','method': 'btn_spvopsapprovalclaim','record_id' : record.id,'message'   : message, 'requirenotes'   : False,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 

    @api.model
    def btn_spvopsrejectclaim(self, ids):
        message ='''it will reject and archieve this claim request. you can create another claim with different request.  are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.claimaccountability','method': 'btn_spvopsrejectclaim','record_id' : record.id,'message'   : message, 'requirenotes'   : True,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    
    @api.model
    def btn_mgropsapprovalclaim(self, ids):
        message ='''it will approve this claim request and [later send it to dynamic 365] For SPV Finance approval, are you sure?''' 
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.claimaccountability','method': 'btn_mgropsapprovalclaim','record_id' : record.id,'message'   : message, 'requirenotes'   : False,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    
    @api.model
    def btn_mgropsrejectclaim(self, ids):
        message ='''it will reject and archieve this claim request. you can create another claim with different request.  are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.claimaccountability','method': 'btn_mgropsrejectclaim','record_id' : record.id,'message'   : message, 'requirenotes'   : True,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    
    @api.model
    def btn_spvfinapprovalclaim(self, ids):
        message ='''it will approve this claim request and [later send it to dynamic 365] For MGR Finance approval, are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.claimaccountability','method': 'btn_spvfinapprovalclaim','record_id' : record.id,'message'   : message, 'requirenotes'   : False,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
     
    @api.model
    def btn_spvfinrejectclaim(self, ids):
        message ='''it will reject and archieve this claim request. you can create another claim with different request.  are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.claimaccountability','method': 'btn_spvfinrejectclaim','record_id' : record.id,'message'   : message, 'requirenotes'   : True,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    
    @api.model
    def btn_mgrfinapprovalclaim(self, ids):
        message ='''it will approve this claim request and [later send it to dynamic 365] finish all claim approval, and proceed to claim payment, are you sure?''' 
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.claimaccountability','method': 'btn_mgrfinapprovalclaim','record_id' : record.id,'message'   : message, 'requirenotes'   : False,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 

    @api.model
    def btn_mgrfinrejectclaim(self, ids):
        message ='''it will reject and archieve this claim request. you can create another claim with different request.  are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.claimaccountability','method': 'btn_mgrfinrejectclaim','record_id' : record.id,'message'   : message, 'requirenotes'   : True,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    
    @api.model
    def btn_claimpaid(self, ids):
        # message ='''it will flag this transaction to Claim Paid, are you sure?'''
        message ='''it will flag this transaction to PLOTREQ/ [Request Korlap untuk plot/assign driver], are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.claimaccountability','method': 'btn_claimpaid','record_id' : record.id,'message'   : message, 'requirenotes'   : False,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    @api.model 
    def button_cancelwithconfirm(self, ids):
        for record_id in ids:
            record = self.browse(record_id)
            message = '''Are you sure you want to cancel record #claimid#? 
                        it will return the workorder(s) collected in this claim form. so it will be used in another claim. but 
                        need to reactivated first by using Workorder menu.
                        after that (for now), it will deletes this claim form.<br \>#wodata#'''
            table       = '''  
                            <table style="width: 100%;" border=1>
                                <tr class="customtable_thback">
                                    <th rowspan="2">Row</th>
                                    <th rowspan="2">woid</th>
                                    <th rowspan="2">dari</th>
                                    <th rowspan="2">ke</th>
                                    <th rowspan="2">biaya</th>
                                    <th colspan="3">before</th>
                                    <th colspan="3">after</th>  
                                </tr>
                                <tr class="customtable_thback"> 
                                    <td>stage </td>
                                    <td>activestage </td>
                                    <td>claimid </td> 
                                    <td>stage </td>
                                    <td>activestage </td>
                                    <td>claimid </td>  
                                </tr>
                                #content#
                            <table> 
                            '''
            datamaster  = '''<tr class="{classe}">
                                <td class="alignright">{Row}            </td>
                                <td>{dwoid}          </td>
                                <td>{qi_locationfrom}</td>
                                <td>{qi_locationto}  </td>
                                <td class="alignright">{qi_cost}        </td>
                                <td>{stage}          </td>
                                <td>{activestage}    </td>
                                <td>{claimid}        </td>
                                <td>{stageaft}       </td>
                                <td>{activestageaft} </td>
                                <td>{claimidaft}     </td> 
                            <tr>''' 
            datacollect = ''; rowcount = 0; classy='customtable_td1'
            if record.draftwo:
                for id in record.draftwo:
                    rowcount = rowcount +1
                    if rowcount % 2 == 0:
                        classy='customtable_td2'
                    else:
                        classy='customtable_td1' 
                    datamastercopy = datamaster.format( classe          =classy             ,   dwoid           =id.dwoid, 
                                                        qi_locationfrom =id.qi_locationfrom ,   qi_locationto   =id.qi_locationto,
                                                        qi_cost         =id.qi_cost         ,   Row             =rowcount,
                                                        stage           =id.stage           ,   activestage     =id.activestage,
                                                        claimid         =id.claimid         ,   stageaft        ='RTC',   
                                                        activestageaft  ='CIC'              ,   claimidaft      ='NULL'         
                                                      )
                    datacollect = datacollect+datamastercopy
            table =table.replace('#content#',datacollect)  
            message = message.replace('#wodata#',table)
            message = message.replace('#claimid#',record.claimid)
            confirm = False
            if not self.env.context.get('confirmed'): 
                confirm = self.env['tl.ms.cuscon'].sudo().create({
                    'message'   : message,
                    'model'     : 'tl.tr.claimaccountability',
                    'method'    : 'button_cancelwithconfirm',
                    'record_id' : record.id,
                })
                return {
                    'type'      : 'ir.actions.act_window',
                    'res_model' : 'tl.ms.cuscon',
                    'view_mode' : 'form',
                    'res_id'    : confirm.id,
                    'target'    : 'new',
                }  
        return {'type': 'ir.actions.act_window_close'}
 