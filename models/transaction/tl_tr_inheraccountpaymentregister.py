from ast import Store
from re import A
from traitlets import default
from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from datetime import date
 
from odoo import models
     
 
class AccountPaymentRegisterApproval(models.Model): 
    
    _name = 'tl.tr.accpytregapproval' #nama di db berubah jadi training_course
    _description = 'Account Payment Register Approval'
    
        
    @api.model
    def create(self, vals):   
        c_initial =''    
        if 'partner_typex' in vals:
            partner_typex = str(vals['partner_typex']) 
            if(partner_typex=='customer'):c_initial='CS'
            if(partner_typex=='supplier'):c_initial='SP'
            vals['idapproval'] = self.env['ir.sequence'].get_per_doc_code(c_initial,'PRA' )  
        # vals['moveid'] =1
        res = super(AccountPaymentRegisterApproval, self).create(vals)
        return res 
    

    # journal_id = fields.Char(default='/', string ='invoice no', readonly = True)    
    idapproval= fields.Char(default='-', string='memo', required=True)   
    account_payment_register = fields.Integer(store=True, readonly=False)   
    journal_idx = fields.Many2one('account.journal', store=True, readonly=False)   
    amountx = fields.Float(default='0', string ='Amount')     
    partner_bank_idx = fields.Many2one('res.partner.bank', store=True, readonly=False)   
    payment_datex = fields.Datetime(string='payment Date',default='2022-01-01', required=True) 
    communicationx = fields.Char(string='memo', required=True)  
    
    partner_typex = fields.Selection(string="partner_type",
    selection=[
    ("customer",  "Customer"),
    ("supplier",  "Supplier") 
    ])  
    currency_idx = fields.Many2one('res.currency', store=True, readonly=False, domain=[('name','=','Rp')])  
    
    stage = fields.Selection(string="stage",
    selection=[
    ("1_Requested",  "Requested"),
    ("2_Verified",  "Verified") ,
    ("3_Approved",  "Approved") ,
    ("x_Declined",  "Declined") 
    ])  
    stage_requestdate = fields.Datetime(string='Request Date') 
    stage_verifieddate = fields.Datetime(string='Verified Date') 
    stage_approveddate = fields.Datetime(string='Approved Date') 
    stage_declineddate = fields.Datetime(string='declined Date') 
    stage_userrequest = fields.Char(string='user Request') 
    stage_userverify = fields.Char(string='user Verified') 
    stage_userapprove = fields.Char(string='user Approved') 
    stage_userdecline = fields.Char(string='usere declined') 


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    approvalinfo = fields.Char(string='approvalinfo', default='-') #field di db 
    approvalnotes = fields.Char(string='approvalnotes',default='-', required=True) #field di db 
    @api.onchange('amount') #onload nih
    def amount_onchange(self):   
        msg='amount onchange'
        # self.amount = 222
        # raise ValidationError(self.amount)
    def get_message_bank(self):
        msg='Jika Recipient Bank Account, <html><b>kosong</b></html>. silahkan input di Invoicing> Configuration>Add Bank Account atau'
        msg=msg+'Settings> User & Companies > Companies >[pilih Mitra Ananta Megah, input dulu kalo belom ada]>klik  link: contact[PT Mitra Ananta Megah]>masuk tab Invoicing>edit bank'
        # raise UserError(msg) s
        action = self.env.ref('base.action_res_company_form')
        raise RedirectWarning(msg, action.id, ('Go to the configuration panel'))

    @api.depends('can_edit_wizard', 'journal_id')
    def _compute_available_partner_bank_ids(self):
        for wizard in self:
            if wizard.can_edit_wizard:
                batch = wizard._get_batches()[0]  
                wizard.available_partner_bank_ids = wizard._get_batch_available_partner_banks(batch, wizard.journal_id)
                
            else:
                wizard.available_partner_bank_ids = None
                
    @api.model
    def _get_batch_available_partner_banks(self, batch_result, journal):
        key_values = batch_result['key_values'] 
        company = batch_result['lines'].company_id

        # A specific bank account is set on the journal. The user must use this one.
        if key_values['payment_type'] == 'inbound':
            # Receiving money on a bank account linked to the journal.
            return journal.bank_account_id
        else:
            # Sending money to a bank account owned by a partner.
            return batch_result['lines'].partner_id.bank_ids.filtered(lambda x: x.company_id.id in (False, company.id))._origin

    def action_request_payments(self):  
        # jurn_obj = self.env['account.journal'].sudo().search([('name','=','Rp')], limit=1) 
        curr_obj = self.env['res.currency'].sudo().search([('name','=','Rp')], limit=1)   #ini dipake sebenernya buat detail 
        user_obj = self.env['res.users'].sudo().search([('id','=',self.env.user.id)], limit=1)   #ini dipake sebenernya buat detail  
        acprid = 0
        for wizard in self:
            acprid = wizard.id 
        self.env['tl.tr.accpytregapproval'].sudo().create({
            'journal_idx':self.journal_id.id, 
            'amountx':self.amount, 
            'partner_bank_idx':self.partner_bank_id.id, 
            'payment_datex':self.payment_date, 
            'communicationx':self.communication, 
            'partner_typex':self.partner_type, 
            'currency_idx':curr_obj.id,
            'stage':'1_Requested',
            'account_payment_register':acprid,
            'stage_requestdate':fields.Date.today(),
            'stage_userrequest':user_obj.partner_id.name})
            

        # msg='action_request_payments'+str(self)
        # raise ValidationError(msg) 
    def action_verify_payments(self):
        msg='action_verify_payments'
        raise ValidationError(msg) 
    def action_approve_payments(self):
        msg='action_approve_payments'
        raise ValidationError(msg) 
    def action_decline_payments(self):
        msg='action_decline_payments'
        raise ValidationError(msg) 
    
    def action_create_payments(self):
        # vals = super().action_create_payments()
        vals = super()._create_payments()  
        # Make sure the account move linked to generated payment
        # belongs to the expected sales team
        # team_id field on account.payment comes from the `_inherits` on account.move model 
        return vals
    def action_create_request_payments(self):
        # vals = super().action_create_payments() 
        vals=1 
        # Make sure the account move linked to generated payment
        # belongs to the expected sales team
        # team_id field on account.payment comes from the `_inherits` on account.move model 
        return vals
