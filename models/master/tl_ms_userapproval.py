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
 

class userapproval(models.Model): #
    _name = 'tl.ms.userapproval' #nama di db berubah jadi training_course
    _description = 'Master userapproval' 
    _rec_name = 'user_id'
    order = fields.Selection(string="order",selection=[("1",  "1"),("2",  "2"),("3",  "3"),("4",  "4"),
                                                       ("5",  "5"),("6",  "6"),("7",  "7"),("8",  "8") ])   
    user_id = fields.Many2one('res.users', string="User" ,domain=[('company_id','=',1)])    
    user_picture = fields.Image(related='user_id.image_128', string="user_picture")
    model=fields.Many2one('ir.model', string="model" ,domain=[('model','in',('account.move','account.payment.register','tl.tr.claimaccountability'))])    
    level = fields.Selection(string="level", selection=[("Requestor"  ,  "Requestor"  ),
                                                        ("Verificator",  "Verificator"),
                                                        ("Approver OPS 1"   ,  "Approver OPS 1"   ),
                                                        ("Approver OPS 2"   ,  "Approver OPS 2"   ),
                                                        ("Approver OPS 3"   ,  "Approver OPS 3"   ),
                                                        ("Approver FNC 1"   ,  "Approver FNC 1"   ),
                                                        ("Approver FNC 2"   ,  "Approver FNC 2"   ),
                                                        ("Approver FNC 3"   ,  "Approver FNC 3"   ),
                                                        ("Uang Jalan Payment"   ,  "Uang Jalan Payment"   ) ]) 

    # _sql_constraints = [
    #                  ('user_id', 
    #                   'unique(user_id)',
    #                   'Choose another value - it has to be unique!')
    #                     ]   
  