from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models 
from odoo.exceptions import UserError, ValidationError

class workorder(models.Model): #
    _name = 'tl.tr.workorder' #nama di db berubah jadi training_course
    _description = 'Transaction workorder' 
    _rec_name       = 'woid'  
    woid = fields.Char(default='/', string ='ref', readonly = True)  
    pullback = fields.Char( readonly = True)  
    

    #coding customer id start 
     
    @api.onchange('draftwo') 
    def defwrite_updatewono(self):#def yang dipakai untuk defwrite, pantang melakuan write() model yang sama
        
        wono = '' 
        for s in self:
            wono = s.woid
            print(wono,'xxxxxxxxxxxxxxxxxxxxx')
            for id in s.draftwo:
                if(id not in (None, False)):
                    dwID = id._origin.id  
                    # draftwo = self.env['tl.tr.draftwo'].search([(id, '=', dwID)]) 
                    # if(draftwo.wono in (False,None)):
                    #     draftwo.sudo().write({'wono':wono,'stage':'DIW',}) 
                    # if(draftwo.stage in ('NEW','DRF')):
                    #     draftwo.sudo().write({'stage':'DIW',})   

    @api.onchange('customerid') 
    def cus_onchange(self):   
        if(self.customerid not in(None,False)):  
            tl_ms_user  = self.env['tl.ms.user'].search([('user_id', '=', self.env.user.id)], limit=1) 
            tl_ms_user.sudo().write({'defaultcustomer':self.customerid.id})  
            self.custinitial = self.customerid.companyinitial 
        return {'domain': {'draftwo': [('customerid', '=', self.customerid.id)]}} 

    @api.onchange('woid') 
    def id_onchange(self): 
        print(self.id,'ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss')
        # import ipdb; ipdb.set_trace()


    def newdefault(self):   
        int_emp = self.getdefaultcustomerid()   
        return int_emp

    customerid = fields.Many2one('res.partner', string='CustomerID' ,required=True, default=newdefault,   domain=[('is_logistic_customer','=',1)])   
        
    def getdefaultcustomerid(self):  
        tl_ms_user  = self.env['tl.ms.user'].search([('user_id', '=', self.env.user.id)], limit=1)    
        if(tl_ms_user.defaultcustomer.id in (False, None) ): 
            tl_ms_user.sudo().create({'user_id':self.env.user.id,'defaultcustomer':self.customerid.id})   
        tl_ms_user  = self.env['tl.ms.user'].search([('user_id', '=', self.env.user.id)], limit=1)    
        result =tl_ms_user.defaultcustomer.id
        return result

    def print_bonputih(self):   
        selected_ids = self.id  
        datas = { 
            'id': selected_ids, 
            'model': 'tl.tr.workorder',
            'data': 'data' [0],
        }
        return self.env.ref('tlsystem.erick_wobonputih_print').report_action(self, data=datas)
#
 
  
    @api.model
    def defcust(self):   
        int_emp = self.getdefaultcustomerid() 
        str_emp = str(int_emp)  
        return str_emp  
 

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
     
  
    defaultcustomer=fields.Integer(default=defcust, string ='defaultcustomer', store=False )        
    iscorrectcust = fields.Boolean(compute='_getcorrectcust',string="iscorrectcust", store=False,search='_value_search')
    custinitial = fields.Char(string='Customer Initial' )    
    #coding customer id end  
 
    draftwo = fields.Many2many('tl.tr.draftwo',  required=True)  
    wodate = fields.Datetime(string='SO Date', required=True) 
    totalSalesPrice  = fields.Float(compute='_amount_totalSalesPrice', string='total Sales Price', readonly = True)
    totalCost  = fields.Float(compute='_amount_totalCost', string='total Cost', readonly = True)
    pullbackable  = fields.Boolean( string='pullbackable', readonly = True)
 
 
    def _amount_totalSalesPrice(self):
        for rec in self:
            total = sum(rec.draftwo.mapped('qi_salesprice')) if rec.draftwo else 0
            rec.totalSalesPrice = total

    def _amount_totalCost(self):
        for rec in self:
            total = sum(rec.draftwo.mapped('qi_cost')) if rec.draftwo else 0
            rec.totalCost = total

    dummy  = fields.Char(string='-', store=False, readonly = True)

    stage = fields.Selection(string="stage", default='DIW', 
    selection=[
    # ("NEW",  "New stage"),
    ("DIW",  "draft in Sales Order"),
    ("RTC",  "Ready To create claim"),
    ("DIC",  "draft in claim"),
    ("CAA",  "Claim Accountability Approved"),
    ("RTI",  "Ready To be Invoiced"),
    ("CWO",  "Canceled in workorder stage") 
    ])  
    def action_confirmready(self): 
        self.stage ='RTI' 
    def action_confirmpullback(self): 
        self.stage ='DIW'
        self.updatedraftwostatus('DIW') 
    # def action_confirmreadytoclaim(self):  
    #     workorder = self.env['tl.tr.workorder'].search([('id', '=', self.id)])
    #     for content in workorder:   
    #         if(content.draftwo not in (False, None)):
    #             for id in content.draftwo:  
    #                 draftwo = self.env['tl.tr.draftwo'].search([('id', '=', id.id)]) 
    #                 draftwo.sudo().write({'stage':'RTC',})    
    #     workorder.sudo().write({'stage':'RTC',})       
    @api.model
    def action_confirmreadytoclaim(self, ids):
        message ='''it will set this Sales Order to be able to request claim. are you sure?'''  
        for record_id in ids:
            record = self.browse(record_id)
            if not self.env.context.get('confirmed'):   
                deletes = self.env['tl.ms.cuscon'].sudo().search([('record_id', '=', record.id)]).sudo().unlink()
                confirm = self.env['tl.ms.cuscon'].sudo().create({'model': 'tl.tr.workorder','method': 'action_confirmreadytoclaim','record_id' : record.id,'message'   : message, })  
                return {'type' : 'ir.actions.act_window','res_model' : 'tl.ms.cuscon','view_mode' : 'form','res_id'    : confirm.id,'target' : 'new',}  
        return  {'type': 'ir.actions.act_window_close'} 

    def action_confirmrevertdraft(self):
        workorder = self.env['tl.tr.workorder'].search([('id', '=', self.id)])
        for content in workorder:   
            if(content.draftwo not in (False, None)):
                for id in content.draftwo:
                    draftwo = self.env['tl.tr.draftwo'].search([('id', '=', id.id)])
                    draftwo.sudo().write({'activestage':'ACT','stage':'DIW','wono':self.woid,})  
        workorder.sudo().write({'stage':'DIW'})     

    def action_confirmcancel(self):    
        workorder = self.env['tl.tr.workorder'].search([('id', '=', self.id)])
        for content in workorder:   
            if(content.draftwo not in (False, None)):
                for id in content.draftwo:
                    draftwo = self.env['tl.tr.draftwo'].search([('id', '=', id.id)])
                    draftwo.sudo().write({'activestage':'CWO','wono':False,})  
        workorder.sudo().write({'draftwo':False,'stage':'CWO'})
                
   
    @api.model
    def unlink(self, vals):    
        for item in vals:  #jangan berusaha ambil ID dari self. gak bakal ada, aneh kan? emang
            tableworkorder = self.env['tl.tr.workorder'].search([('id', '=', item)])
            stage= tableworkorder.stage; errmsg =False 
            if(stage=="CWO")             : errmsg="[tl.tr.draftwo]ini sudah berstatus canceled in workorder stage"
            if(stage not in("DIW","NEW")): errmsg="[tl.tr.draftwo]kamu gak bisa hapus workorder kecuali dalam status DRAFT/NEW, dan hanya akan berubah ke status CANCELED"+str(stage)
            if(errmsg!= False):raise ValidationError(errmsg)   
            if(tableworkorder.draftwo not in (False, None)):
                for id in tableworkorder.draftwo:
                    draftwo = self.env['tl.tr.draftwo'].search([('id', '=', id.id)])
                    draftwo.sudo().write({'activestage':'CWO','wono':False,}) 
            tableworkorder.sudo().write({'draftwo':False,'stage':'CWO'})  
            # workorder = self.env['tl.tr.workorder'].search([('id', '=', tableworkorder.id)])
            # workorder.sudo().write({'stage':'CWO'})    
        # 3# return res

    @api.model
    def updatedraftwostatus(self, stage):#ini dipakai hanya saat tombol di click.which sudah punya ID 
        if(self.draftwo not in (False, None)):
            for id in self.draftwo:
                draftwo = self.env['tl.tr.draftwo'].search([('id', '=', id)])
                if(stage=='CWO'): 
                    draftwo.sudo().write({'stage':stage,'wono':False,}) 
                else:
                    draftwo.sudo().write({'stage':stage,})  
 


    @api.model
    def deletequotid(self, wono):
        if(self.draftwo not in (False, None)):
            for id in self.draftwo:
                draftwo = self.env['tl.tr.draftwo'].search([('id', '=', id)]) 
                draftwo.sudo().write({'wono':False,'activestage':'CWO',})  
        
    @api.model
    def defcreate_updatewono(self, vals):   
        # if(self.draftwo.id not in (False, None)): #def create kadang tricky, gw buat dua2nya aja
        #     for id in self.draftwo: 
        #         draftwo = self.env['tl.tr.draftwo'].search([('id', '=', id)]) 
        #         draftwo.sudo().write({'wono':wono,'stage':'DIW',})   
        vdwo= vals.get('draftwo'); wono= vals.get('woid')
        if(vdwo not in (None, False)): 
            for id in vdwo: 
                list = (id[2])
                for idx in list: 
                    draftwo = False
                    a=0; e = 'EE'
                    try: draftwo =self.env['tl.tr.draftwo'].search([('id', '=', idx)]) 
                    except Exception as e: 
                        print('sistem rusak')
                    else:  
                        if(draftwo!=False):
                            draftwo.sudo().write({'wono':wono,'stage':'DIW',})    
                    
                # try: iter(column)
                # except TypeError: print(column,"Object not an iterable")
                # else: 
                #     if(item_index==3): iterable_draftwo = column 
        # import ipdb; ipdb.set_trace()

    @api.model
    def create(self, vals):      
        self.defcreate_validasicustomer(vals)
        c_initial =  vals.get('custinitial')
        woid= self.env['ir.sequence'].get_short_master(c_initial, 'SO'); vals['woid'] =woid  ; vals['stage'] ='DIW'  
        res = super(workorder, self).create(vals) 
        self.defcreate_updatewono(vals)
        return res 
  

    # def defwrite_updatewonodeleteaja(self):
    #     wono = '' 
    #     for s in self:
    #         wono = s.woid
    #         print(wono,'xxxxxxxxxxxxxxxxxxxxx')
    #         for id in s.draftwo:
    #             if(id not in (None, False)):
    #                 dwID = id._origin.id  
    #                 # draftwo = self.env['tl.tr.draftwo'].search([(id, '=', dwID)]) 
    #                 # if(draftwo.wono in (False,None)):
    #                 #     draftwo.sudo().write({'wono':wono,'stage':'DIW',}) 
    #                 # if(draftwo.stage in ('NEW','DRF')):
    #                 #     draftwo.sudo().write({'stage':'DIW',})   
                    


    def write(self, vals):      
        self.defwrite_validasicustomer(vals)
        stage =''
        errmsg='' 
        custidhd =  vals.get('customerid')
        if(custidhd == None):
            custidhd =  self.customerid.id 
        custidhdtable  =  self.env['res.partner'].sudo().search([('id','=',custidhd)])   
        for f in self: #dah pasti 1x looping doang kecuali dari paging
            woid = str(f.woid)    #ini diipake kalo pas update. jangan ketuker  
            stage=vals.get('stage') 
            action= 'none'
            if(stage=="NEW"):
                ax="WR01 - New Stage" 
            elif(stage=="DIW"): action= 'update'
            elif(stage=="RTC"): action= 'update'
            elif(stage=="RTI"): action= 'updateRTI'
            elif(stage=="CWO"): action= 'cancel'
            elif(stage=='NEW' or stage=='DIW'):
                f.stage ='DIW' 
                action= 'update'
            elif(stage==None):   #stage_tidak_berubah
                action= 'update'
            else:
                action= 'hold'    
            if(action=='hold'):
                msg = '[tl.tr.workorder]_status sudah bukan di NEW atau DRAFT, tidak bisa di edit lagi. status='+stage+', woidHD='+woid 
                raise ValidationError(msg)  
            if(action in('cancel','update')): 
                res = super(workorder, self).write(vals)    
                for id in self.draftwo: 
                    if(id.wono == False): id.sudo().update({'wono':woid})  
                return res  
            if(action=='updateRTI'):
                res = super(workorder, self).write(vals)  
                contact = self.env['tl.tr.draftwo'].search([('wono', '=', self.woid)])
                for content in contact:   
                    sqlstring = """ update tl_tr_draftwo set stage='RTI' where id = """+str(content.id)+""";""" 
                    self._cr.execute(sqlstring)    
                return res 

    def defwrite_validasicustomer(self, vals):  
        draftwo = vals.get('draftwo'); iterable_draftwo = False; item_index = 0; msg = False; result = True 
        if(draftwo not in (None,False)):
            for cover in draftwo:
                for column in cover:  
                    item_index = item_index+1
                    try: iter(column)
                    except TypeError: print(column,"Object not an iterable")
                    else: 
                        if(item_index==3): iterable_draftwo = column 
                        
            # vdwo= vals.get('draftwo')
            # if(vdwo not in(None, False)):
            #     for id in vdwo: 
            #         list = (id[2])
            #         for idx in list:
            #             table  =  self.env['tl.tr.draftwo'].sudo().search([('id','=',idx)])  
            if(len(list(iterable_draftwo)) ==0):
                raise ValidationError('draftwo tidak ditemukan, jangan di save dulu, harus ada isinya')   
            if(iterable_draftwo == False):
                raise ValidationError('draftwo tidak ditemukan, iterable_draftwo =False')   
            for id in iterable_draftwo: 
                tbldwo = self.env['tl.tr.draftwo'].sudo().search([('id','=',id)])     
                hdcust = self.customerid.id; dtcust = tbldwo.customerid.id
                hdcustname = self.env['tl.tr.draftwo'].sudo().search([('id','=',hdcust)]).customerid.name    
                dtcustname = tbldwo.customerid.name 
                if(hdcust !=dtcust):msg = 'anda sedang memilih customer: ['+str(hdcustname)+'], silahkan  pilihdraft wo yang sesuai. karena nomor:#DWO# adalah transaksi milik customer:['+str(dtcustname)+'], silahkan di revisi datanya'
                elif(tbldwo.stage       not in ('NEW','DRF' )): msg = 'stage [#DWO#]-['+str(tbldwo.stage)+'] yang anda  pilih berada diluar stage yang boleh dipakai untuk membuat workorder. hanya boleh di [NEW, DRF]. silahkan revisi data yang anda pilih'
                elif(tbldwo.activestage not in ('ACT'       )): msg = 'tltrworkorder defwrite:activestage [#DWO#]-['+str(tbldwo.activestage)+'] yang anda  pilih berada diluar activestage yang boleh dipakai untuk membuat workorder. hanya boleh di [ACT]. silahkan revisi data yang anda pilih'
                elif(tbldwo.invoiceno   !=          False    ): msg = 'tltrworkorder defwrite:nomor [#DWO#] sudah berada dalam invoice ['+str(tbldwo.invoiceno)+'] tidak bisa dibuatkan workorder  lagi.'
                elif(tbldwo.wono        !=          False    ): msg = 'tltrworkorder defwrite:nomor [#DWO#] sudah berada dalam workorder ['+str(tbldwo.wono)+'] tidak bisa dibuatkan workorder  lagi.'
                if(msg != False):
                    result = False; msg= msg.replace('#DWO#',tbldwo.dwoid)
                    raise ValidationError(msg)     


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
            elif(tbldwo.stage       not in ('NEW','DRF' )): msg = 'tltrworkorder:stage [#DWO#]-['+str(tbldwo.stage)+'] yang anda  pilih berada diluar stage yang boleh dipakai untuk membuat workorder. hanya boleh di [NEW, DRF]. silahkan revisi data yang anda pilih'
            elif(tbldwo.activestage not in ('ACT'       )): msg = 'tltrworkorder:activestage [#DWO#]-['+str(tbldwo.activestage)+'] yang anda  pilih berada diluar activestage yang boleh dipakai untuk membuat workorder. hanya boleh di [ACT]. silahkan revisi data yang anda pilih'
            elif(tbldwo.invoiceno   !=          False    ): msg = 'tltrworkorder:nomor [#DWO#] sudah berada dalam invoice ['+str(tbldwo.invoiceno)+'] tidak bisa dibuatkan workorder  lagi.'
            elif(tbldwo.wono        !=          False    ): msg = 'tltrworkorder:nomor [#DWO#] sudah berada dalam workorder ['+str(tbldwo.wono)+'] tidak bisa dibuatkan workorder  lagi.'
            if(msg != False):
                result = False; msg= msg.replace('#DWO#',tbldwo.dwoid)
                raise ValidationError(msg)     

         
    @api.model
    def updatedraft(self, wono): 
            for id in self.draftwo:
                draftwo = self.env['tl.tr.draftwo'].search([('id', '=', id)]) 
                draftwo.sudo().write({'wono':wono,'stage':'DIW',})  
            wo = self.env['tl.tr.workorder'].search([('id', '=', self.id)]) 
            wo.sudo().write({'stage':'DIW',})    