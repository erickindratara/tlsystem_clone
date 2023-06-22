from odoo import api, fields, models
 
 
class InvoiceWizard(models.TransientModel):
    _name = 'invoice.wizard'
    _description = 'Invoice Wizard'
  
    def _default_sesi(self):
        return self.env['tl.tr.invoice'].browse(self._context.get('active_ids'))

        
            # cust = self.env['tl.ms.customer'].sudo().browse(vals['customerid'])
    invoice_id = fields.Many2one('tl.tr.invoice', string="invoice", default=_default_sesi)
    draftwo_ids = fields.Many2many('tl.tr.draftwo', string='draftwo')
    def tambah_peserta(self):
        self.invoice_id.invoiceno |= self.draftwo_ids