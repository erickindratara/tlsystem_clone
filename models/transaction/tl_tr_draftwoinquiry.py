from ast import Store
from cgitb import text
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from typing_extensions import Required
from venv import create
from weakref import ref
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class draftwoinquiry(models.TransientModel): #
    
    _name = 'tl.tr.draftwoinquiry' #nama di db berubah jadi training_course
    _description = 'Transaction Draft WO inquiry' 
    # ref = fields.Char(default='/', string ='ref', readonly = True) 
    
    # _inherits = {'tl.tr.draftwo': 'manfactureyear'}
    