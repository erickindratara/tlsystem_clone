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
 
 
class modulestage(models.Model): #
    _name = 'tl.ms.modulestage' #nama di db berubah jadi training_course
    _description = 'Master Module Stage'
    _rec_name = 'modulename' 
    
    modulename = fields.Many2one('tl.ms.modulelist', string="modulename")  #field di db
    orders = fields.Integer(string='order integer(2)', size=2)
    stage = fields.Char(string='stage varchar(3)', size=3)
    stagedesc = fields.Char(string='stagedesc varchar(30)', size=30)  