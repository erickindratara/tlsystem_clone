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
  
class pertanggungjawabanapproval(models.Model): #
    _name           = 'tl.tr.pertanggungjawabanapproval' #nama di db berubah jadi training_course
    _description    = 'approval pertanggungjawaban'   
    parent_id       = fields.Integer(string='parent_id', default='' )  
    sequence        = fields.Integer(string='seq', default='' )    
    userapproval    = fields.Many2one('tl.ms.userapproval')    
    approvallevel   = fields.Char(string='Approval level' )   
    approvaldate    = fields.Datetime(string='Action Date') 
    approvalnote    = fields.Text(string='approvalnote', default='' )    
    pjid         = fields.Text(string='pjid', default='' )    
     

    def unlink(self):     
        res = super(pertanggungjawabanapproval, self).unlink()  
        return res   
    
    def write(self, vals):    
        res = super(pertanggungjawabanapproval, self).write(vals)  
        return res   
    
    @api.model
    def create(self, vals):      
        res     = super(pertanggungjawabanapproval, self).create(vals) 
        return res 
    
class pertanggungjawaban(models.Model): 
    _name        = 'tl.tr.pertanggungjawaban'  
    _description = 'pertanggungjawaban Transaction'  
    _rec_name             = 'pjid'   
    pjid                  = fields.Char(string='pertanggungjawaban ID', default='/' )    
    counts                = fields.Integer(compute='_compute_counts', string='WO Count'   ,store=False)
    sumcost               = fields.Integer(compute='_compute_counts', string='Total Cost' ,store=False)
    sumclaim              = fields.Integer(compute='_compute_counts', string='Total Uang Jalan',store=False)
    sumpertanggungjawaban = fields.Integer(compute='_compute_counts', string='Total Pertanggung Jawaban',store=False)
    approval              = fields.Many2many('tl.tr.pertanggungjawabanapproval')         
    currentapprover       = fields.Boolean(compute='_iscurrentapprover',string="iscurrentapprover", store=False)  
    @api.model
    def _iscurrentapprover(self):     
        for record in self:  
            iscurrentapprover = False  
            order = 0
            currstage = self.stage  
            if(currstage =="DIP"        ):order = 1# "Draft Pertanggungjawaban"
            if(currstage =="REQ-PJ/OP1" ):order = 2# "Req App Pertanggungjawaban OPS SPV"
            if(currstage =="REQ-PJ/OP2" ):order = 3# "Req App Pertanggungjawaban OPS MGR"
            if(currstage =="REQ-PJ/FN1" ):order = 4# "Req App Pertanggungjawaban FNC SPV"
            if(currstage =="REQ-PJ/FN2" ):order = 5# "Req App Pertanggungjawaban FNC MGR"
            if(currstage =="PJPAID"     ):order = 6# "Selisih Pertanggungjawaban Has Been Paid"

            curruser= self.env['tl.ms.userapproval'].search([('model.model' ,'=', 'tl.tr.pertanggungjawaban'),
                                                             ('user_id'     ,'=', self.env.user.id),
                                                             ('order'       ,'=', order),
                                                             ], limit=1)   
            for id in curruser:
                if(id.id): iscurrentapprover = True  
            record['currentapprover'] = iscurrentapprover

    @api.depends('draftwo')
    def _compute_counts(self):         
        for record in self: 
            record.counts                   =  len(record.draftwo)  
            record.sumcost                  =  sum(record.draftwo.mapped('qi_cost'))
            record.sumclaim                 =  sum(record.draftwo.mapped('claimamount'))  
            record.sumpertanggungjawaban    =  sum(record.draftwo.mapped('claimaccountabilityamount'))   
  
    def cekdefaultfilter(self):  
        ir_filters = self.env['ir.filters'].sudo(); ir_filters.search([('model_id', '=', 'tl.tr.pertanggungjawaban')]).sudo().unlink()  
        ir_filters.sudo().create({ 
            'model_id'  : 'tl.tr.pertanggungjawaban'   ,'name'      : "stage in New, Draft. Group by Send Date"   ,
            'active'    : 'True'                        ,'domain'    : '[]'  , 
            'sort'      : "[]"            ,'context'   : "{'group_by': ['customerid','stage','senddate:week']}",
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
        return {'domain': {'draftwo': ['&',('wono', '!=', False),('stage', 'in', ('RTP','MBL/DRVDNE')),('customerid', '=', self.customerid.id)]}}
   
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
     

    pertanggungjawabandate =fields.Datetime(string='Tanggal Pertanggung Jawaban', required=True, default=fields.Datetime.now)

    draftwo = fields.Many2many('tl.tr.draftwo',  required=True)  
        
    stage = fields.Selection(string="stage", default="NEW", 
            selection=[ ("NEW"       ,                            "Newly Created"),
                        ("DIP"       ,                 "Draft Pertanggungjawaban"),    
                        ("REQ-PJ/OP1",       "Req App Pertanggungjawaban OPS SPV"),
                        ("APV-PJ/OP1",                         "OPS SPV Approved"),
                        ("REQ-PJ/OP2",       "Req App Pertanggungjawaban OPS MGR"), 
                        ("APV-PJ/OP2",                         "OPS MGR Approved"),
                        ("REQ-PJ/FN1",       "Req App Pertanggungjawaban FNC SPV"),
                        ("APV-PJ/FN1",                         "FNC SPV Approved"), 
                        ("REQ-PJ/FN2",       "Req App Pertanggungjawaban FNC MGR"),
                        ("APV-PJ/FN2",                         "FNC MGR Approved"),  
                        ("APV-PJ/COM",    "Approval Pertanggungjawaban Completed"),   
                        ("PJPAID"    , "Selisih Pertanggungjawaban Has Been Paid"),    
                        ("PJRTD"     ,  "Pertanggungjawaban Ready To Dynamic 365"),    
                        ("CIP"       ,                        "Canceled/Rejected")
                        ])  
    @api.onchange('claimaccountabilitydate')
    def all_onchange(self):  
        if(self.stage=='NEW'):
            self.stage ='DIP' 
  
    def defcreate_validasicustomer(self, vals): 
        draftwo = vals.get('draftwo'); iterable_draftwo = False; item_index = 0; msg = False; result = True
        if(draftwo != None): 
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
                if(hdcust !=dtcust):msg = 'anda sedang memilih customer: ['+str(hdcustname)+'], silahkan  pilih Sales Order yang sesuai. karena nomor:#DWO# adalah transaksi milik customer:['+str(dtcustname)+'], silahkan di revisi datanya'
                elif(tbldwo.stage       not in ('RTP','MBL/DRVDNE')): msg = '4 stage [#DWO#]-['+str(tbldwo.stage)+'] yang anda  pilih berada diluar stage yang boleh dipakai untuk membuat pertanggungjawaban. hanya boleh di [RTP- Ready to Create Pertanggungjawaban]. silahkan revisi data yang anda pilih'
                elif(tbldwo.activestage not in ('ACT'       )): msg = '3 activestage [#DWO#]-['+str(tbldwo.activestage)+'] yang anda  pilih berada diluar activestage yang boleh dipakai untuk membuat claim. hanya boleh di [ACT]. silahkan revisi data yang anda pilih'
                elif(tbldwo.invoiceno   !=          False    ): msg = '2 nomor [#DWO#] sudah berada dalam invoice ['+str(tbldwo.invoiceno)+'] tidak bisa dibuatkan claim  lagi.'
                elif(tbldwo.pjid     !=          False    ): msg = '1 nomors [#DWO#] sudah berada dalam pertanggungjawaban ['+str(tbldwo.pjid)+'] tidak bisa dibuatkan pertanggungjawaban lagi.'
                if(msg != False):
                    result = False; msg= msg.replace('#DWO#',tbldwo.dwoid)
                    raise ValidationError(msg)     
        else:
                raise ValidationError('draftwo nya masih kosong om')   


    @api.model
    def create(self, vals):   
        self.defcreate_validasicustomer(vals)

        c_initial =  vals.get('custinitial')
        if(c_initial in (None, False)):
            c_initial = self.env['tl.ms.user'].search([('user_id', '=', self.env.user.id)], limit=1).defaultcustomer.companyinitial   
            vals['custinitial'] =c_initial 
        pjid = self.env['ir.sequence'].get_short_master(c_initial, 'PJ'); vals['pjid'] =pjid  ; vals['stage'] ='DIP'   
        res     = super(pertanggungjawaban, self).create(vals)
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
        res = super(pertanggungjawaban, self).write(vals) 
        return res
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
                    currentpjid = vals.get('pjid') or self.pjid 
                    dw_record   = self.env['tl.tr.draftwo'].search([('id', '=', dew_id)]); hdcust = vals.get('customerid'); msg =False
                    if not hdcust: hdcust = self.customerid.id 
                    hdcustname  = self.env['tl.tr.draftwo'].sudo().search([('customerid','=',hdcust)]).customerid.name; dtcustname = dw_record.customerid.name
                    if hdcust  != dw_record.customerid.id      : msg = 'anda sedaaang memilih customer: [{hdcustname}], silahkan pilih sales order yang sesuai. karena nomor:{dwo_id} adalah transaksi milik customer:[{dtcustname}], silahkan di revisi datanya';msg = msg.format(hdcustname=hdcustname, dwo_id=dw_record.dwoid, dtcustname=dtcustname)
                    elif dw_record.stage  not in ('RTP','DIP',): msg = 'stage [{dwo_id}]-[{stage}] yang anda pilih berada diluar stage yang boleh dipakai untuk membuat/edit pertanggungjawaban. hanya boleh di [RTP- Ready to create Pertanggung Jawaban]. silahkan revisi data yang anda pilih'; msg = msg.format(dwo_id=dw_record.dwoid, stage=dw_record.stage) 
                    elif dw_record.activestage  not in ('ACT',): msg = 'activestage [{dwo_id}]-[{activestage}] yang anda pilih berada diluar activestage yang boleh dipakai untuk membuat Pertanggung Jawaban. hanya boleh di [ACT]. silahkan revisi data yang anda pilih';msg = msg.format(dwo_id=dw_record.dwoid, activestage=dw_record.activestage) 
                    elif dw_record.invoiceno                   : msg = 'nomor [{dwo_id}] sudah berada dalam212 {type} [{num}] tidak bisa dibuatkan Pertanggung Jawaban lagi.'; msg = msg.format(dwo_id=dw_record.dwoid, type='invoice', num=dw_record.invoiceno) 
                    elif not (dw_record.pjid == False or dw_record.pjid == currentpjid): msg = 'nomor [{dwo_id}] sudah berada dalam222 PJ [{num}] yg baru = [{currentpjid}]tidak bisa dibuatkan Pertanggung Jawaban lagi.'; msg = msg.format(dwo_id=dw_record.dwoid,num=dw_record.pjid,currentpjid=currentpjid) 
                    
                    if(msg!=False):
                        raise ValidationError(msg)  
            
    @api.model
    def defwrite_updatewono(self, vals):      
        for s in self:
            vdwo= s.draftwo;  pjid=s.pjid  
            if(vdwo not in (None, False)): 
                for id in vdwo:   
                        draftwo = False 
                        draftwo =self.env['tl.tr.draftwo'].search([('id', '=', id.id)])     
                        if(draftwo!=False and draftwo.stage in ('RTC','DIP')):
                            if(draftwo.stage =='RTC'):
                                draftwo.sudo().write({'pjid':pjid,'stage':'DIP'}) 
                            if(draftwo.stage =='DIP'):
                                draftwo.sudo().write({'pjid':pjid}) 
                            
                       
 
         
    @api.model
    def defcreate_updatewono(self, vals):    
        
        vdwo= vals.get('draftwo'); pjid= vals.get('pjid') 
        if(vdwo not in (None, False) and pjid not in (None, False)): 
            for id in vdwo:  
                list = (id[2])
                for idx in list:  
                    draftwo = False
                    e = 'EE'
                    try: idx = int(idx)
                    except Exception as e: 
                        print('skip')
                    else:  
                        self.env.cr.execute("UPDATE tl_tr_draftwo SET pjid = %s WHERE id = %s", (pjid, idx)) 
 
 
    def unlink(self):          
        if (len(self) > 1): 
            raise ValidationError('Bulk delete is not allowed. Please delete records one by one.') 
        else:  
            for record_id in self: 
                claim_aa =  self.env['tl.tr.pertanggungjawaban'].sudo().browse(record_id.id) 
                stage = claim_aa.stage  
                if stage in ('NEW', 'DIP','CIC','CIP','CIV'): 
                    if not claim_aa.draftwo:                        
                        oktodeletethis=True   
                    else:     
                        draftwo = self.env['tl.tr.draftwo'].sudo().search([('id', 'in', claim_aa.draftwo.ids)])
                        draftwo_list = draftwo.mapped('id') 
                        for row in draftwo: 
                            self.env['tl.tr.draftwo'].sudo().search([('id', '=', row.id)]).sudo().write({'stage': 'RTP','activestage': 'CIP','pjid': False,}) 
            claim_aa.sudo().write({'stage': 'CIP','draftwo': False,})   #it will clear the data first 
            res = super(pertanggungjawaban, self).unlink()
            return res 
         
    @api.model  
    def button_sameasuangjalan(self, ids):
        for record_id in ids:
            record = self.browse(record_id)
            if(record.stage=='DIP'):
                for id in record.draftwo: 
                    tbl_dw = self.env['tl.tr.draftwo'].sudo().search([('id', '=', id.id)])
                    tbl_dw.sudo().update({'claimaccountabilityamount': tbl_dw.claimamount})
            else:
                msg = "cannot update claimaccountabilityamount, only works in DIP (Draft In Draft in Pertanggungjawaban) Stage."
                raise ValidationError(msg) 
  
    @api.model
    def btn_debughapusapproval(self, ids):
        message ='''it will send this approval to non existence, are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.pertanggungjawaban','method': 'btn_debughapusapproval','record_id' : record.id,'message'   : message, 'requirenotes'   : False, })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 

    @api.model
    def btn_reqapprovalpj(self, ids):
        message ='''btn_reqapprovalpj: it will send this to approval, are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.pertanggungjawaban','method': 'btn_reqapprovalpj','record_id' : record.id,'message'   : message, 'requirenotes'   : False,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    @api.model
    def btn_spvopsapprovalpj(self, ids): 
        message ='''it will approve this pertanggungjawaban request and send this to OPS MGR approval, are you sure?''' 
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.pertanggungjawaban','method': 'btn_spvopsapprovalpj','record_id' : record.id,'message'   : message, 'requirenotes'   : False,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 

    @api.model
    def btn_spvopsrejectpj(self, ids):
        message ='''it will reject and archieve this pertanggungjawaban request. you can create another pertanggungjawaban with different request.  are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.pertanggungjawaban','method': 'btn_spvopsrejectpj','record_id' : record.id,'message'   : message, 'requirenotes'   : True,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    
    @api.model
    def btn_mgropsapprovalpj(self, ids):
        message ='''it will approve this pertanggungjawaban request and send it to SPV Finance approval, are you sure?''' 
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.pertanggungjawaban','method': 'btn_mgropsapprovalpj','record_id' : record.id,'message'   : message, 'requirenotes'   : False,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    
    @api.model
    def btn_mgropsrejectpj(self, ids):
        message ='''it will reject and archieve this pertanggungjawaban request. you can create another pertanggungjawaban with different request.  are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.pertanggungjawaban','method': 'btn_mgropsrejectpj','record_id' : record.id,'message'   : message, 'requirenotes'   : True,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    
    @api.model
    def btn_spvfinapprovalpj(self, ids):
        message ='''it will approve this pertanggungjawaban request and send it to MGR Finance approval, are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.pertanggungjawaban','method': 'btn_spvfinapprovalpj','record_id' : record.id,'message'   : message, 'requirenotes'   : False,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
     
    @api.model
    def btn_spvfinrejectpj(self, ids):
        message ='''it will reject and archieve this pertanggungjawaban request. you can create another pertanggungjawaban with different request.  are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.pertanggungjawaban','method': 'btn_spvfinrejectpj','record_id' : record.id,'message'   : message, 'requirenotes'   : True,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    
    @api.model
    def btn_mgrfinapprovalpj(self, ids):
        message ='''it will approve this pertanggungjawaban request and  send it to finish all pertanggungjawaban approval, and proceed to pertanggungjawaban payment, are you sure?''' 
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.pertanggungjawaban','method': 'btn_mgrfinapprovalpj','record_id' : record.id,'message'   : message, 'requirenotes'   : False,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 

    @api.model
    def btn_mgrfinrejectpj(self, ids):
        message ='''it will reject and archieve this pertanggungjawaban request. you can create another pertanggungjawaban with different request.  are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.pertanggungjawaban','method': 'btn_mgrfinrejectpj','record_id' : record.id,'message'   : message, 'requirenotes'   : True,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 
    
    @api.model
    def btn_pjpaid(self, ids):
        message ='''it will flag this transaction to pertanggungjawaban Paid, are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.pertanggungjawaban','method': 'btn_pjpaid','record_id' : record.id,'message'   : message, 'requirenotes'   : False,  })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 

    # @api.model 
    def button_cancelpjwithconfirm(self):
        ids = self.ids
        for record_id in ids:
            record = self.browse(record_id)
            message = '''Are you sure you want to cancel record #pjid#? 
                        it will return the workorder(s) collected in this pertanggungjawaban form. so it will be used in another pertanggungjawaban. but 
                        need to reactivated first by using Workorder menu.
                        after that (for now), it will deletes this pertanggungjawaban form.<br \>#wodata#'''
            table       = '''  
                            <table style="width: 100%;" border=1>
                                <tr class="customtable_thback">
                                    <th rowspan="2">Row</th>
                                    <th rowspan="2">woid</th>
                                    <th rowspan="2">dari</th>
                                    <th rowspan="2">ke</th>
                                    <th rowspan="2">biaya</th>
                                    <th rowspan="2">uang jalan</th>
                                    <th rowspan="2">pertanggungjawaban</th>
                                    <th colspan="3">before</th>
                                    <th colspan="3">after</th>  
                                </tr>
                                <tr class="customtable_thback"> 
                                    <td>stage </td>
                                    <td>activestage </td>
                                    <td>pjid </td> 
                                    <td>stage </td>
                                    <td>activestage </td>
                                    <td>pjid </td>  
                                </tr>
                                #content#
                            <table> 
                            '''
            datamaster  = '''<tr class="{classe}">
                                <td class="alignright">{Row}            </td>
                                <td>{dwoid}          </td>
                                <td>{qi_locationfrom}</td>
                                <td>{qi_locationto}  </td>
                                <td class="alignright">{qi_cost}      </td>
                                <td class="alignright">{claimamt}     </td>
                                <td class="alignright">{pjamt}        </td>
                                <td>{stage}          </td>
                                <td>{activestage}    </td>
                                <td>{pjid}        </td>
                                <td>{stageaft}       </td>
                                <td>{activestageaft} </td>
                                <td>{pjidaft}     </td> 
                            <tr>''' 
            datacollect = ''; rowcount = 0; classy='customtable_td1'
            if record.draftwo:
                for id in record.draftwo:
                    rowcount = rowcount +1
                    if rowcount % 2 == 0:
                        classy='customtable_td2'
                    else:
                        classy='customtable_td1' 
                    pjamt = str(f"{int(id.claimaccountabilityamount ):,}"); var_qicost = str(f"{int(id.qi_cost ):,}"); var_claimamt = str(f"{int(id.claimamount ):,}")
                    datamastercopy = datamaster.format( classe          =classy                         ,   dwoid           =id.dwoid           , 
                                                        qi_locationfrom =id.qi_locationfrom             ,   qi_locationto   =id.qi_locationto   ,
                                                        qi_cost         =var_qicost                     ,   claimamt        =id.claimamount     ,    
                                                        pjamt           =pjamt   ,   Row             =rowcount           ,
                                                        stage           =id.stage                       ,   activestage     =id.activestage     ,
                                                        pjid            =id.pjid                        ,   stageaft        ='RTP'              ,   
                                                        activestageaft  ='CIP'                          ,   pjidaft         ='NULL'         
                                                      )
                    datacollect = datacollect+datamastercopy
            table =table.replace('#content#',datacollect)  
            message = message.replace('#wodata#',table)
            message = message.replace('#pjid#',record.pjid)
            confirm = False
            if not self.env.context.get('confirmed'): 
                confirm = self.env['tl.ms.cuscon'].sudo().create({
                    'message'   : message,
                    'model'     : 'tl.tr.pertanggungjawaban',
                    'method'    : 'button_cancelpjwithconfirm',
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
 