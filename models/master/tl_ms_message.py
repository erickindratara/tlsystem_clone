# from openerp.osv import fields,osv
# from osv import fields, osv
# from openerp.tools.translate import _
from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class thesis_approval_message_oric(models.TransientModel):
    # _name = "thesis.approval.message.oric"
    _name = "tl.ms.message"
    # _columns={
    #     'text': fields.text(),
    # }

    text = fields.Char(stored=False,   readonly=True)
    is_approve = fields.Boolean()
    def btn_approve_oric(self):
        # raw = self.env['tl.ms.message'].search([('id', '=', self.id)]) 
        query ='update tl_ms_message set is_approve= False '#where  id ='+str(self.id)
        self.env.cr.execute(query) 
    
thesis_approval_message_oric() 