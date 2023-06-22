from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from typing_extensions import Required
from venv import create
from weakref import ref
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class modulelist(models.Model): #
    _name = 'tl.ms.modulelist' #nama di db berubah jadi training_course
    _description = 'Master Module list'
    _rec_name = 'modulename' 

    moduletype = fields.Selection(string="module type", required = True, selection=[("MASTER", "Master"), ("TRANS", "Transaction"), ("REPORT", "Report") ])
    modulename = fields.Char(string="module name", required = True)
    attachment1 = fields.Binary('attachment1')
    attachment2 = fields.Binary('attachment2')
    attachment3 = fields.Binary('attachment3')
    attachment4 = fields.Binary('attachment4')
    attachment5 = fields.Binary('attachment5') 
    attachment1_name = fields.Char('attachment1 filename')
    attachment2_name = fields.Char('attachment2 filename')
    attachment3_name = fields.Char('attachment3 filename')
    attachment4_name = fields.Char('attachment4 filename')
    attachment5_name = fields.Char('attachment5 filename') 
    filter = fields.Many2many('ir.filters',  resquired=True) 
 