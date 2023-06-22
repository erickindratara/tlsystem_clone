from odoo import models, fields, api , _ 
from odoo.exceptions import UserError, ValidationError 
from datetime import datetime

 
class cuscon(models.Model):
    _name = 'tl.ms.cuscon'
    _description = 'Custom Confirmation'

    message     = fields.Text(string='Message')
    requirenotes= fields.Boolean(string='requirenotes')
    rejectreason= fields.Text(string='Reject Reason', required=False )
    model       = fields.Char(string='Model')
    method      = fields.Char(string='Method')
    record_id   = fields.Integer(string='Record ID')

    def write(self, vals):   
        res = super(cuscon, self).write(vals) 
        return res
    @api.model
    def create(self, vals):     
        res = super(cuscon, self).create(vals) 
        return res 

    def userselection(self, model, button):
        usercommon = self.env['res.users'].sudo().browse(self.env.user.id); result = False
        # untuk debug start
        # admin_user = self.env['res.users'].sudo().search([('login', '=', '081807902390'),('id', '=', self.env.user.id)], limit=1)
        # if(len(admin_user)>0): 
        # untuk debug end
        if model == 'tl.tr.claimaccountability' :
            user =self.env['tl.ms.userapproval'].sudo().search([('user_id', '=', usercommon.id), ('model.model', '=', model)])
            currentuser = ''
            if button == 'button_cancelwithconfirm': currentuser = user.sudo().search([('user_id.login', '=', '081807902390')], limit=99)
            if button == 'btn_debughapusapproval'  : currentuser = user.sudo().search([('user_id.login', '=', '081807902390')], limit=99)
            if button == 'btn_reqapprovalclaim'    : currentuser = user.sudo().search([('order', '=', 1)], limit=99)
            if button == 'btn_spvopsapprovalclaim' : currentuser = user.sudo().search([('order', '=', 2)], limit=99)
            if button == 'btn_mgropsapprovalclaim' : currentuser = user.sudo().search([('order', '=', 3)], limit=99)
            if button == 'btn_spvfinapprovalclaim' : currentuser = user.sudo().search([('order', '=', 4)], limit=99)
            if button == 'btn_mgrfinapprovalclaim' : currentuser = user.sudo().search([('order', '=', 5)], limit=99)
            if button == 'btn_claimpaid'           : currentuser = user.sudo().search([('order', '=', 6)], limit=99)
            if button == 'btn_spvopsrejectclaim'   : currentuser = user.sudo().search([('order', '=', 2)], limit=99)
            if button == 'btn_mgropsrejectclaim'   : currentuser = user.sudo().search([('order', '=', 3)], limit=99)
            if button == 'btn_spvfinrejectclaim'   : currentuser = user.sudo().search([('order', '=', 4)], limit=99)
            if button == 'btn_mgrfinrejectclaim'   : currentuser = user.sudo().search([('order', '=', 5)], limit=99)
               
            if len(currentuser) > 0: 
                result= True
            else:
                alloweduser = self.env['tl.ms.userapproval'].sudo().search([('model.model', '=', model), ('order', '=', 1)], limit=99)
                listallowed = [record.user_id.partner_id.name for record in alloweduser]
                allowed_str = ', '.join(listallowed)
                msg = f"{usercommon.partner_id.name}/currentuser:{currentuser}/button:{button} kamu tidak memiliki hak akses untuk melakukan request approval uang jalan. silahkan hubungi admin untuk membuka akses, saat ini {allowed_str} yang dapat melakukan request. [press escape key to continue]"
                raise ValidationError(msg) 
        elif model == 'tl.tr.pertanggungjawaban' :
            user =self.env['tl.ms.userapproval'].sudo().search([('user_id', '=', usercommon.id), ('model.model', '=', model)])
            currentuser = ''
            if button == 'button_cancelpjwithconfirm': currentuser = user.sudo().search([('user_id.login', '=', '081807902390')], limit=99)
            if button == 'btn_debughapusapproval'    : currentuser = user.sudo().search([('user_id.login', '=', '081807902390')], limit=99)
            if button == 'btn_reqapprovalpj'         : currentuser = user.sudo().search([('order', '=', 1)], limit=99)
            if button == 'btn_spvopsapprovalpj'      : currentuser = user.sudo().search([('order', '=', 2)], limit=99)
            if button == 'btn_mgropsapprovalpj'      : currentuser = user.sudo().search([('order', '=', 3)], limit=99)
            if button == 'btn_spvfinapprovalpj'      : currentuser = user.sudo().search([('order', '=', 4)], limit=99)
            if button == 'btn_mgrfinapprovalpj'      : currentuser = user.sudo().search([('order', '=', 5)], limit=99)
            if button == 'btn_pjpaid'                : currentuser = user.sudo().search([('order', '=', 6)], limit=99)
            if button == 'btn_spvopsrejectpj'        : currentuser = user.sudo().search([('order', '=', 2)], limit=99)
            if button == 'btn_mgropsrejectpj'        : currentuser = user.sudo().search([('order', '=', 3)], limit=99)
            if button == 'btn_spvfinrejectpj'        : currentuser = user.sudo().search([('order', '=', 4)], limit=99)
            if button == 'btn_mgrfinrejectpj'        : currentuser = user.sudo().search([('order', '=', 5)], limit=99)
               
            if len(currentuser) > 0: 
                result= True
            else:
                alloweduser = self.env['tl.ms.userapproval'].sudo().search([('model.model', '=', model), ('order', '=', 1)], limit=99)
                listallowed = [record.user_id.partner_id.name for record in alloweduser]
                allowed_str = ', '.join(listallowed)
                msg = f"{usercommon.partner_id.name}/currentuser:{currentuser}/button:{button} kamu tidak memiliki hak akses untuk melakukan request approval pertanggungjawaban. silahkan hubungi admin untuk membuka akses, saat ini {allowed_str} yang dapat melakukan request. [press escape key to continue]"
                raise ValidationError(msg) 
        else:  
            raise ValidationError('tl.ms.cuscon.py: userselection() model tidak dikenal')     
        return result
    def generatematrix(self, record_id): 
        self.env['tl.tr.claimaccountabilityapproval'].sudo().search([('parent_id', '=', record_id)]).sudo().unlink()
        claim_accountability= self.env['tl.tr.claimaccountability'].sudo().browse(record_id)
        sum_cost            = sum(record.qi_cost        for record in claim_accountability.draftwo)
        sum_amountclaim     = sum(record.claimamount    for record in claim_accountability.draftwo)
        msg                 = False
        if  (sum_amountclaim >sum_cost ): msg= 'sum amount uang jalan ('+str(f"{int(sum_amountclaim):,}")+') lebih besar dari cost (' +str(f"{int(sum_cost):,}")+'), pertimbangkan aja dulu'
        elif(sum_amountclaim ==0 )      : msg= 'sum amount uang jalan ('+str(f"{int(sum_amountclaim):,}")+') tidak boleh NOL '
        if(msg!=False): raise ValidationError(msg) 
        else:       
            claim_accountability.draftwo.sudo().update({'stage':'REQ-C/OP1'})
            claim_accountability.sudo().write({'stage':'REQ-C/OP1'})
            claim_accountability_approvals = self.env['tl.tr.claimaccountabilityapproval'].sudo().search([('parent_id', '=', record_id)])
            user_approvals = self.env['tl.ms.userapproval'].sudo().search([('model.model', '=', 'tl.tr.claimaccountability')], order='order ASC')
            last_level = False
            sequence = 0
            for user_approval in user_approvals:
                if last_level != user_approval.level:
                    last_level = user_approval.level
                    sequence += 1
                    claim_accountability_approvals.sudo().create({
                        'parent_id'     : record_id ,'approvallevel' : user_approval.level,
                        'userapproval'  : False     ,'approvalnote'  : 'waiting action1',
                        'sequence'      : sequence  ,'claimid'       : claim_accountability.claimid,})
            
            claim_accountability_approvals = self.env['tl.tr.claimaccountabilityapproval'].sudo().search([('parent_id', '=', record_id)])
            claim_accountability.sudo().write({'approval': claim_accountability_approvals}) 
        
    def generatematrixpj(self, record_id): 
        self.env['tl.tr.pertanggungjawabanapproval'].sudo().search([('parent_id', '=', record_id)]).sudo().unlink()
        pertanggungjawaban  = self.env['tl.tr.pertanggungjawaban'].sudo().browse(record_id)
        sum_cost            = sum(record.qi_cost                    for record in pertanggungjawaban.draftwo)
        sum_amountclaim     = sum(record.claimamount                for record in pertanggungjawaban.draftwo)
        sum_amountpj        = sum(record.claimaccountabilityamount  for record in pertanggungjawaban.draftwo)
        msg                 = False
        if  (sum_amountpj> sum_amountclaim ): msg= 'sum amount uang jalan ('+str(f"{int(sum_amountpj):,}")+') lebih besar dari uangjalan (' +str(f"{int(sum_amountclaim):,}")+'), pertimbangkan aja dulu'
        elif(sum_amountpj==0               ): msg= 'sum amount PJ         ('+str(f"{int(sum_amountpj):,}")+') tidak boleh NOL '
        if(msg!=False): raise ValidationError(msg) 
        else:       
            pertanggungjawaban.draftwo.sudo().update({'stage':'REQ-PJ/OP1'})
            pertanggungjawaban.sudo().write({'stage':'REQ-PJ/OP1'})
            pertanggungjawaban_approvals = self.env['tl.tr.pertanggungjawabanapproval'].sudo().search([('parent_id', '=', record_id)])
            user_approvals = self.env['tl.ms.userapproval'].sudo().search([('model.model', '=', 'tl.tr.pertanggungjawaban')], order='order ASC')
            if len(user_approvals)==0: 
                msg = ('master approval tidak ada, silahkan jalankan:','insert into tl_ms_userapproval (user_id, model, level, create_uid, create_date, write_uid, write_date, "order")'
                        'select  user_id, 7094, level, create_uid, create_date, write_uid, write_date, "order" from tl_ms_userapproval where model=6947 '
                        'order by "order" asc ;'
                        'update tl_ms_userapproval set level = ''Selisih Uang Pertanggungjawaban Paid'' where level = ''Uang Jalan Payment'' and model =7094'
                        )

                raise ValidationError(msg)
            else:
                last_level = False
                sequence = 0
                for user_approval in user_approvals:
                    if last_level != user_approval.level:
                        last_level = user_approval.level
                        sequence += 1
                        pertanggungjawaban_approvals.sudo().create({
                            'parent_id'     : record_id ,'approvallevel' : user_approval.level,
                            'userapproval'  : False     ,'approvalnote'  : 'waiting action1',
                            'sequence'      : sequence  ,'pjid'          : pertanggungjawaban.pjid,})
                
                pertanggungjawaban_approvals = self.env['tl.tr.pertanggungjawabanapproval'].sudo().search([('parent_id', '=', record_id)])
                pertanggungjawaban.sudo().write({'approval': pertanggungjawaban_approvals}) 
        
        
    def debughapusapproval(self, record_id): 
        self.env['tl.tr.claimaccountabilityapproval'].sudo().search([('parent_id', '=', record_id)]).sudo().unlink()
        self.env['tl.tr.claimaccountability'].sudo().browse(record_id).sudo().write({'approval': False,'stage': 'DIC', })  
        self.env['tl.tr.claimaccountability'].sudo().browse(record_id).draftwo.sudo().update({'stage':'DIC'})
    def debughapusapprovalpj(self, record_id): 
        self.env['tl.tr.pertanggungjawabanapproval'].sudo().search([('parent_id', '=', record_id)]).sudo().unlink()
        self.env['tl.tr.pertanggungjawaban'].sudo().browse(record_id).sudo().write({'approval': False,'stage': 'DIP', })  
        self.env['tl.tr.pertanggungjawaban'].sudo().browse(record_id).draftwo.sudo().update({'stage':'DIP'})
    
    def flaggingmatrix(self, conid,  sequence, isreject):   
        cuscon=self.env['tl.ms.cuscon'].sudo().search([('id', '=', conid)]) 
        record_id = cuscon.record_id; rejnotes = cuscon.rejectreason
        bah_user = self.env['tl.ms.userapproval'].sudo().search([('user_id', '=', self.env.user.id)], limit=1); approvalnote = ''
        first_approval_record = self.env['tl.tr.claimaccountabilityapproval'].sudo().search([('parent_id', '=', record_id),])
        if(isreject==False):
            if(sequence ==1): approvalnote = 'Request Uang Jalan created' ;self.generatematrix(record_id)
            if(sequence ==2): approvalnote = 'OPS 1 Approved' 
            if(sequence ==3): approvalnote = 'OPS 2 Approved'
            if(sequence ==4): approvalnote = 'FNC 1 Approved'
            if(sequence ==5): approvalnote = 'FNC 2 Approved'
            if(sequence ==6): approvalnote = 'Uang Jalan has been Transfered' 
            first_approval_record=first_approval_record.sudo().search([('sequence', '=', sequence)])
            first_approval_record.sudo().write({'userapproval': bah_user.id, 'approvaldate': fields.Datetime.now(), 'approvalnote': approvalnote})
        if(isreject==True):  
            if(sequence ==2): approvalnote = 'OPS 1 Rejected, reason: '+ str(rejnotes)
            if(sequence ==3): approvalnote = 'OPS 2 Rejected, reason: '+ str(rejnotes) 
            if(sequence ==4): approvalnote = 'FNC 1 Rejected, reason: '+ str(rejnotes) 
            if(sequence ==5): approvalnote = 'FNC 2 Rejected, reason: '+ str(rejnotes)  
            first_approval_record=first_approval_record.sudo().search([('sequence', '=', sequence)])
            first_approval_record.sudo().write({'userapproval': bah_user.id, 'approvaldate': fields.Datetime.now(), 'approvalnote': approvalnote})
            first_approval_record=first_approval_record.sudo().search([('sequence', '>', sequence)])
            first_approval_record.sudo().write({'approvalnote': 'rejected'})
        
    def flaggingmatrixpj(self, conid,  sequence, isreject):   
        cuscon=self.env['tl.ms.cuscon'].sudo().search([('id', '=', conid)]) 
        record_id = cuscon.record_id; rejnotes = cuscon.rejectreason
        bah_user = self.env['tl.ms.userapproval'].sudo().search([('user_id', '=', self.env.user.id)], limit=1); approvalnote = ''
        first_approval_record = self.env['tl.tr.pertanggungjawabanapproval'].sudo().search([('parent_id', '=', record_id),])
        if(isreject==False):
            if(sequence ==1): approvalnote = 'Request pertanggungjawaban created' ; self.generatematrixpj(record_id)
            if(sequence ==2): approvalnote = 'OPS 1 Approved' 
            if(sequence ==3): approvalnote = 'OPS 2 Approved'
            if(sequence ==4): approvalnote = 'FNC 1 Approved'
            if(sequence ==5): approvalnote = 'FNC 2 Approved'
            if(sequence ==6): approvalnote = 'Pertanggung jawaban has been completed' 
            first_approval_record=first_approval_record.sudo().search([('sequence', '=', sequence)])
            first_approval_record.sudo().write({'userapproval': bah_user.id, 'approvaldate': fields.Datetime.now(), 'approvalnote': approvalnote})
        if(isreject==True):  
            if(sequence ==2): approvalnote = 'OPS 1 Rejected, reason: '+ str(rejnotes) 
            if(sequence ==3): approvalnote = 'OPS 2 Rejected, reason: '+ str(rejnotes) 
            if(sequence ==4): approvalnote = 'FNC 1 Rejected, reason: '+ str(rejnotes) 
            if(sequence ==5): approvalnote = 'FNC 2 Rejected, reason: '+ str(rejnotes)  
            first_approval_record=first_approval_record.sudo().search([('sequence', '=', sequence)])
            first_approval_record.sudo().write({'userapproval': bah_user.id, 'approvaldate': fields.Datetime.now(), 'approvalnote': approvalnote})
            first_approval_record=first_approval_record.sudo().search([('sequence', '>', sequence)])
            first_approval_record.sudo().write({'approvalnote': 'rejected'})
        
    @api.model
    def action_confirm(self,  vals):   
        for id in vals:
            cuscon=self.env['tl.ms.cuscon'].sudo().search([('id', '=', id)]) 
            if(cuscon.model =='tl.tr.claimaccountability'):
                ttca_hd = self.env['tl.tr.claimaccountability'].sudo().search([('id', '=', cuscon.record_id)])
                userberhak = self.userselection(cuscon.model,cuscon.method) 
                if(userberhak):
                    conid = cuscon.id; rcid = cuscon.record_id; method = cuscon.method 
                    if  (method =='button_cancelwithconfirm'):ttca_hd.sudo().unlink()
                    elif(method =='btn_debughapusapproval'  ):self.debughapusapproval(cuscon.record_id)
                    elif(method =='btn_reqapprovalclaim'    ):self.flaggingmatrix(conid,1,False) 
                    elif(method =='btn_spvopsapprovalclaim' ):self.flaggingmatrix(conid,2,False);stage='REQ-C/OP2';ttca_hd.sudo().write({'stage':stage}); ttca_hd.draftwo.sudo().update({'stage':stage})
                    elif(method =='btn_mgropsapprovalclaim' ):self.flaggingmatrix(conid,3,False);stage='REQ-C/FN1';ttca_hd.sudo().write({'stage':stage}); ttca_hd.draftwo.sudo().update({'stage':stage}) 
                    elif(method =='btn_spvfinapprovalclaim' ):self.flaggingmatrix(conid,4,False);stage='REQ-C/FN2';ttca_hd.sudo().write({'stage':stage}); ttca_hd.draftwo.sudo().update({'stage':stage})
                    elif(method =='btn_mgrfinapprovalclaim' ):self.flaggingmatrix(conid,5,False);stage='APV-C/COM';ttca_hd.sudo().write({'stage':stage}); ttca_hd.draftwo.sudo().update({'stage':stage})
                    # elif(method =='btn_claimpaid'           ):self.flaggingmatrix(conid,6,False);stage='RTP'      ;ttca_hd.sudo().write({'stage':stage}); ttca_hd.draftwo.sudo().update({'stage':stage})
                    elif(method =='btn_claimpaid'           ):self.flaggingmatrix(conid,6,False);stage='PLOTREQ'      ;ttca_hd.sudo().write({'stage':stage}); ttca_hd.draftwo.sudo().update({'stage':stage})
                    elif(method =='btn_spvopsrejectclaim'   ):self.flaggingmatrix(conid,2,True );stage='CIC'      ;ttca_hd.sudo().write({'stage':stage}); ttca_hd.draftwo.sudo().update({'stage':'RTC','claimid':False,})
                    elif(method =='btn_mgropsrejectclaim'   ):self.flaggingmatrix(conid,3,True );stage='CIC'      ;ttca_hd.sudo().write({'stage':stage}); ttca_hd.draftwo.sudo().update({'stage':'RTC','claimid':False,})
                    elif(method =='btn_spvfinrejectclaim'   ):self.flaggingmatrix(conid,4,True );stage='CIC'      ;ttca_hd.sudo().write({'stage':stage}); ttca_hd.draftwo.sudo().update({'stage':'RTC','claimid':False,})
                    elif(method =='btn_mgrfinrejectclaim'   ):self.flaggingmatrix(conid,5,True );stage='CIC'      ;ttca_hd.sudo().write({'stage':stage}); ttca_hd.draftwo.sudo().update({'stage':'RTC','claimid':False,})
                                    
                    else: 
                        raise ValidationError('well.. nothing will be executed. please check your code') 
                else: 
                    raise ValidationError('kamu tidak berhak', cuscon.method) 
            if(cuscon.model =='tl.tr.pertanggungjawaban'):
                ttpj_hd = self.env['tl.tr.pertanggungjawaban'].sudo().search([('id', '=', cuscon.record_id)])
                userberhak = self.userselection(cuscon.model,cuscon.method) 
                
                if(userberhak):
                    conid = cuscon.id; rcid = cuscon.record_id; method = cuscon.method 
                    if  (method =='button_cancelpjwithconfirm'):ttpj_hd.sudo().unlink()
                    elif(method =='btn_debughapusapproval'    ):self.debughapusapprovalpj(cuscon.record_id)
                    elif(method =='btn_reqapprovalpj'         ):self.flaggingmatrixpj(conid,1,False) 
                    elif(method =='btn_spvopsapprovalpj'      ):self.flaggingmatrixpj(conid,2,False);stage='REQ-PJ/OP2';ttpj_hd.sudo().write({'stage':stage}); ttpj_hd.draftwo.sudo().update({'stage':stage})
                    elif(method =='btn_mgropsapprovalpj'      ):self.flaggingmatrixpj(conid,3,False);stage='REQ-PJ/FN1';ttpj_hd.sudo().write({'stage':stage}); ttpj_hd.draftwo.sudo().update({'stage':stage}) 
                    elif(method =='btn_spvfinapprovalpj'      ):self.flaggingmatrixpj(conid,4,False);stage='REQ-PJ/FN2';ttpj_hd.sudo().write({'stage':stage}); ttpj_hd.draftwo.sudo().update({'stage':stage})
                    elif(method =='btn_mgrfinapprovalpj'      ):self.flaggingmatrixpj(conid,5,False);stage='APV-PJ/COM';ttpj_hd.sudo().write({'stage':stage}); ttpj_hd.draftwo.sudo().update({'stage':stage})
                    elif(method =='btn_pjpaid'                ):self.flaggingmatrixpj(conid,6,False);stage='PJRTD'     ;ttpj_hd.sudo().write({'stage':stage}); ttpj_hd.draftwo.sudo().update({'stage':stage})
                    elif(method =='btn_spvopsrejectpj'        ):self.flaggingmatrixpj(conid,2,True );stage='CIP'       ;ttpj_hd.sudo().write({'stage':stage}); ttpj_hd.draftwo.sudo().update({'stage':'RTP','pjid':False,})
                    elif(method =='btn_mgropsrejectpj'        ):self.flaggingmatrixpj(conid,3,True );stage='CIP'       ;ttpj_hd.sudo().write({'stage':stage}); ttpj_hd.draftwo.sudo().update({'stage':'RTP','pjid':False,})
                    elif(method =='btn_spvfinrejectpj'        ):self.flaggingmatrixpj(conid,4,True );stage='CIP'       ;ttpj_hd.sudo().write({'stage':stage}); ttpj_hd.draftwo.sudo().update({'stage':'RTP','pjid':False,})
                    elif(method =='btn_mgrfinrejectpj'        ):self.flaggingmatrixpj(conid,5,True );stage='CIP'       ;ttpj_hd.sudo().write({'stage':stage}); ttpj_hd.draftwo.sudo().update({'stage':'RTP','pjid':False,})       
                    else: 
                        raise ValidationError('well.. nothing will be executed. please check your code') 
                else: 
                    raise ValidationError('kamu tidak berhak', cuscon.method) 
                
            if(cuscon.model =='tl.tr.workorder'):
                ttwo = self.env['tl.tr.workorder'].sudo().search([('id', '=', cuscon.record_id)])
                if(cuscon.method =='action_confirmreadytoclaim'):     
                    if(len(ttwo.draftwo) ==0):
                        raise ValidationError('tidak ada isinya, tidak bisa di proses')
                    ttwo.draftwo.sudo().update({'stage':'RTC',})    
                    ttwo.sudo().update({'stage':'RTC',})            
                else: 
                    raise ValidationError('well.. nothing will be executed. please check your code') 
            
        return {'type': 'ir.actions.act_window_close'}
