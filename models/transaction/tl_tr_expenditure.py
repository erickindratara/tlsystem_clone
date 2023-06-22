from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models 
from odoo.exceptions import UserError, ValidationError


class expenditure(models.Model): #
    _name = 'tl.tr.expenditure' #nama di db berubah jadi training_course
    _description = 'Transaction expenditure'
    ref =fields.Char(default='EHD',readonly=True)
     
    customerid = fields.Many2one('tl.tr.expenditure', string="expenditure")   
    name = fields.Char(string='Name', required=True) #field di db 
    description = fields.Char(string='description', required=True) #field di db  
    cost = fields.Float(string='Cost', required=True) #field di db  
    @api.model
    def csreate(self, vals):
        if 'customerid' in vals:
            cust = self.env['tl.ms.customer'].sudo().browse(vals['customerid'])
            vals['ref'] = self.env['ir.sequence'].get_per_doc_code(cust.companyinitial, 'EDT')

        return super(expenditure, self).create(vals)