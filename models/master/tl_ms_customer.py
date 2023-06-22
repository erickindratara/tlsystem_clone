from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models 
 
class customer(models.Model): #
    _name = 'tl.ms.customer' #nama di db berubah jadi training_course
    _description = 'Master Customer'
    _rec_name = 'name'
    name = fields.Char(string='Company Name', required=True) #field di db  
    companyinitial = fields.Char(string='Company Initial', required=True) #field di db 
    termofpayment = fields.Selection(string="TOP", selection=[("14", "14 hr"),  ("15", "15 hr") ]) 
    isactive = fields.Boolean(string='is Active', required=True) #field di db   
    PIC = fields.Many2many('tl.ms.user', 'tl_ms_customer_pic', string="PIC users")  
    # customerid = fields.One2many('tl.ms.customer', 'id', string="Customer")   
    # PIC = fields.One2many(comodel_name="tl.ms.user",  inverse_name="user_id",  string="PIC users",  help="")


  
  