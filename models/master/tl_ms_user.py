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
 

class users(models.Model): #
    _name = 'tl.ms.user' #nama di db berubah jadi training_course
    _description = 'Master user'
    _rec_name = 'user_id'
    user_id = fields.Many2one('res.users', string="User")    
    user_picture = fields.Image(related='user_id.image_128', string="user_picture")
     

    defaultcustomer = fields.Many2one('res.partner', string='Default Customer' , domain=[('is_company','=',True),('is_logistic_customer','=',True)],   store=True) 
    
    cust_image = fields.Image(related='defaultcustomer.image_128') 
    _sql_constraints = [
                     ('user_id', 
                      'unique(user_id)',
                      'Choose another value - it has to be unique!')
                        ]   
  